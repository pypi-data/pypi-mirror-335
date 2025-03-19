# -*- coding: utf-8; -*-
#
# Licensed to MonkDB Labs Private Limited (MonkDB) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  MonkDB licenses
# this file to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may
# obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.

import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time

import urllib3

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen  # type: ignore[attr-defined,no-redef]


log = logging.getLogger(__name__)


MONKDB_CONFIG_ERROR = (
    'monkdb_config must point to a folder or to a file named "monkdb.yml"'
)
HTTP_ADDRESS_RE = re.compile(
    r".*\[(http|.*HttpServer.*)\s*] \[.*\] .*"
    "publish_address {"
    r"(?:inet\[[\w\d\.-]*/|\[)?"
    r"(?:[\w\d\.-]+/)?"
    r"(?P<addr>[\d\.:]+)"
    r"(?:\])?"
    "}"
)


def http_url_from_host_port(host, port):
    if host and port:
        if not isinstance(port, int):
            try:
                port = int(port)
            except ValueError:
                return None
        return "{}:{}".format(prepend_http(host), port)
    return None


def prepend_http(host):
    if not re.match(r"^https?\:\/\/.*", host):
        return "http://{}".format(host)
    return host


def _download_and_extract(uri, directory):
    sys.stderr.write(
        "\nINFO:    Downloading MonkDB archive from {} into {}".format(
            uri, directory
        )
    )
    sys.stderr.flush()
    with io.BytesIO(urlopen(uri).read()) as tmpfile:
        with tarfile.open(fileobj=tmpfile) as t:
            t.extractall(directory)


def wait_for_http_url(log, timeout=30, verbose=False):
    start = time.monotonic()
    while True:
        line = log.readline().decode("utf-8").strip()
        elapsed = time.monotonic() - start
        if verbose:
            sys.stderr.write("[{:>4.1f}s]{}\n".format(elapsed, line))
        m = HTTP_ADDRESS_RE.match(line)
        if m:
            return prepend_http(m.group("addr"))
        elif elapsed > timeout:
            return None


class OutputMonitor:
    def __init__(self):
        self.consumers = []

    def consume(self, iterable):
        for line in iterable:
            for consumer in self.consumers:
                consumer.send(line)

    def start(self, proc):
        self._stop_out_thread = threading.Event()
        self._out_thread = threading.Thread(
            target=self.consume, args=(proc.stdout,)
        )
        self._out_thread.daemon = True
        self._out_thread.start()

    def stop(self):
        if self._out_thread is not None:
            self._stop_out_thread.set()
            self._out_thread.join()


class LineBuffer:
    def __init__(self):
        self.lines = []

    def send(self, line):
        self.lines.append(line.strip())


class MonkDBLayer:
    """
    This layer starts a MonkDB server.
    """

    __bases__ = ()

    tmpdir = tempfile.gettempdir()
    wait_interval = 0.2

    @staticmethod
    def from_uri(
        uri,
        name,
        http_port="4200-4299",
        transport_port="4300-4399",
        settings=None,
        directory=None,
        cleanup=True,
        verbose=False,
    ):
        """Download the MonkDB tarball from a URI and create a MonkDBLayer

        :param uri: The uri that points to the MonkDB tarball
        :param name: layer and cluster name
        :param http_port: The http port on which MonkDB will listen
        :param transport_port: the transport port on which MonkDB will listen
        :param settings: A dictionary that contains MonkDB settings
        :param directory: Where the tarball will be extracted to.
                          If this is None a temporary directory will be created.
        :param clean: a boolean indicating if the directory should be removed
                      on teardown.
        :param verbose: Set the log verbosity of the test layer
        """
        directory = directory or tempfile.mkdtemp()
        filename = os.path.basename(uri)
        monkdb_dir = re.sub(r"\.tar(\.gz)?$", "", filename)
        monkdb_home = os.path.join(directory, monkdb_dir)

        if os.path.exists(monkdb_home):
            sys.stderr.write(
                "\nWARNING: Not extracting MonkDB tarball"
                " because folder already exists"
            )
            sys.stderr.flush()
        else:
            _download_and_extract(uri, directory)

        layer = MonkDBLayer(
            name=name,
            monkdb_home=monkdb_home,
            port=http_port,
            transport_port=transport_port,
            settings=settings,
            verbose=verbose,
        )
        if cleanup:
            tearDown = layer.tearDown

            def new_teardown(*args, **kws):
                shutil.rmtree(directory)
                tearDown(*args, **kws)

            layer.tearDown = new_teardown  # type: ignore[method-assign]
        return layer

    def __init__(
        self,
        name,
        monkdb_home,
        monkdb_config=None,
        port=None,
        keepRunning=False,
        transport_port=None,
        monkdb_exec=None,
        cluster_name=None,
        host="127.0.0.1",
        settings=None,
        verbose=False,
        env=None,
    ):
        """
        :param name: layer name, is also used as the cluser name
        :param monkdb_home: path to home directory of the monkdb installation
        :param port: port on which monkdb should run
        :param transport_port: port on which transport layer for monkdb should
                               run
        :param monkdb_exec: alternative executable command
        :param monkdb_config: alternative monkdb config file location.
                             Must be a directory or a file named 'monkdb.yml'
        :param cluster_name: the name of the cluster to join/build. Will be
                             generated automatically if omitted.
        :param host: the host to bind to. defaults to 'localhost'
        :param settings: further settings that do not deserve a keyword
                         argument will be prefixed with ``es.``.
        :param verbose: Set the log verbosity of the test layer
        :param env: Set environment variables.
        """
        self.__name__ = name
        if settings and isinstance(settings, dict):
            # extra settings may override host/port specification!
            self.http_url = http_url_from_host_port(
                settings.get("network.host", host),
                settings.get("http.port", port),
            )
        else:
            self.http_url = http_url_from_host_port(host, port)

        self.process = None
        self.verbose = verbose
        self.env = env or {}
        self.env.setdefault("MONKDB_USE_IPV4", "true")
        self.env.setdefault("JAVA_HOME", os.environ.get("JAVA_HOME", ""))
        self._stdout_consumers = []
        self.conn_pool = urllib3.PoolManager(num_pools=1)

        monkdb_home = os.path.abspath(monkdb_home)
        if monkdb_exec is None:
            start_script = "monkdb.bat" if sys.platform == "win32" else "monkdb"
            monkdb_exec = os.path.join(monkdb_home, "bin", start_script)
        if monkdb_config is None:
            monkdb_config = os.path.join(monkdb_home, "config", "monkdb.yml")
        elif (
            os.path.isfile(monkdb_config)
            and os.path.basename(monkdb_config) != "monkdb.yml"
        ):
            raise ValueError(MONKDB_CONFIG_ERROR)
        if cluster_name is None:
            cluster_name = "Testing{0}".format(port or "Dynamic")
        settings = self.create_settings(
            monkdb_config,
            cluster_name,
            name,
            host,
            port or "4200-4299",
            transport_port or "4300-4399",
            settings,
        )
        # ES 5 cannot parse 'True'/'False' as booleans so convert to lowercase
        start_cmd = (monkdb_exec,) + tuple(
            [
                "-C%s=%s"
                % (
                    (key, str(value).lower())
                    if isinstance(value, bool)
                    else (key, value)
                )
                for key, value in settings.items()
            ]
        )

        self._wd = wd = os.path.join(MonkDBLayer.tmpdir, "monkdb_layer", name)
        self.start_cmd = start_cmd + ("-Cpath.data=%s" % wd,)

    def create_settings(
        self,
        monkdb_config,
        cluster_name,
        node_name,
        host,
        http_port,
        transport_port,
        further_settings=None,
    ):
        settings = {
            "discovery.type": "zen",
            "discovery.initial_state_timeout": 0,
            "node.name": node_name,
            "cluster.name": cluster_name,
            "network.host": host,
            "http.port": http_port,
            "path.conf": os.path.dirname(monkdb_config),
            "transport.tcp.port": transport_port,
        }
        if further_settings:
            settings.update(further_settings)
        return settings

    def wdPath(self):
        return self._wd

    @property
    def monkdb_servers(self):
        if self.http_url:
            return [self.http_url]
        return []

    def setUp(self):
        self.start()

    def _clean(self):
        if os.path.exists(self._wd):
            shutil.rmtree(self._wd)

    def start(self):
        self._clean()
        self.process = subprocess.Popen(
            self.start_cmd, env=self.env, stdout=subprocess.PIPE
        )
        returncode = self.process.poll()
        if returncode is not None:
            raise SystemError(
                "Failed to start server rc={0} cmd={1}".format(
                    returncode, self.start_cmd
                )
            )

        if not self.http_url:
            # try to read http_url from startup logs
            # this is necessary if no static port is assigned
            self.http_url = wait_for_http_url(
                self.process.stdout, verbose=self.verbose
            )

        self.monitor = OutputMonitor()
        self.monitor.start(self.process)

        if not self.http_url:
            self.stop()
        else:
            sys.stderr.write("HTTP: {}\n".format(self.http_url))
            self._wait_for_start()
            self._wait_for_master()
            sys.stderr.write("\nMonkDB instance ready.\n")

    def stop(self):
        self.conn_pool.clear()
        if self.process:
            self.process.terminate()
            self.process.communicate(timeout=10)
            self.process.stdout.close()
            self.process = None
        self.monitor.stop()
        self._clean()

    def tearDown(self):
        self.stop()

    def _wait_for(self, validator):
        start = time.monotonic()

        line_buf = LineBuffer()
        self.monitor.consumers.append(line_buf)

        while True:
            wait_time = time.monotonic() - start
            try:
                if validator():
                    break
            except Exception as e:
                self.stop()
                raise e

            if wait_time > 30:
                for line in line_buf.lines:
                    log.error(line)
                self.stop()
                raise SystemError("Failed to start MonkDB instance in time.")
            sys.stderr.write(".")
            time.sleep(self.wait_interval)

        self.monitor.consumers.remove(line_buf)

    def _wait_for_start(self):
        """Wait for instance to be started"""

        # http may be ready before the cluster
        # is fully available block here so that early requests
        # after the layer starts don't result in 503
        def validator():
            try:
                resp = self.conn_pool.request("HEAD", self.http_url)
                return resp.status == 200
            except Exception:
                return False

        self._wait_for(validator)

    def _wait_for_master(self):
        """Wait for master node"""

        def validator():
            resp = self.conn_pool.urlopen(
                "POST",
                "{server}/_sql".format(server=self.http_url),
                headers={"Content-Type": "application/json"},
                body='{"stmt": "select master_node from sys.cluster"}',
            )
            data = json.loads(resp.data.decode("utf-8"))
            return resp.status == 200 and data["rows"][0][0]

        self._wait_for(validator)

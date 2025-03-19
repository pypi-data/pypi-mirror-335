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

"""
MonkDB Client Library

This module provides an HTTP-based client for interacting with MonkDB's API.
It includes utilities for making SQL queries, handling authentication, managing
server pools, and interacting with MonkDB's blob storage.

Modules and Features:
----------------------
- MonkClient: The primary client class for interacting with MonkDB.
- MonkServer: Handles individual MonkDB server connections.
- JSON serialization utilities for handling datetime and decimal data types.
- Connection pooling and server failover mechanisms.
- MonkDB-specific exception handling.

Dependencies:
-------------
- urllib3: HTTP connection handling
- orjson: Fast JSON serialization
- verlib2: Version management
- monkpy.client.exceptions: MonkDB-specific exceptions
"""

import calendar
import datetime as dt
import heapq
import io
import logging
import os
import re
import socket
import ssl
import threading
import typing as t
from base64 import b64encode
from decimal import Decimal
from time import time
from urllib.parse import urlparse

import orjson
import urllib3
from urllib3 import connection_from_url
from urllib3.connection import HTTPConnection
from urllib3.exceptions import (
    HTTPError,
    MaxRetryError,
    ProtocolError,
    ProxyError,
    ReadTimeoutError,
    SSLError,
)
from urllib3.util.retry import Retry
from verlib2 import Version

from monkdb.client.exceptions import (
    MonkBlobLocationNotFoundException,
    MonkConnectionError,
    MonkDigestNotFoundException,
    MonkIntegrityError,
    MonkProgrammingError,
)

logger = logging.getLogger(__name__)


_HTTP_PAT = pat = re.compile("https?://.+", re.I)
SERVICE_UNAVAILABLE_STATUSES = {502, 503, 504, 509}
PRESERVE_ACTIVE_SERVER_EXCEPTIONS = {ConnectionResetError, BrokenPipeError}
SSL_ONLY_ARGUMENTS = {"ca_certs", "cert_reqs", "cert_file", "key_file"}


def super_len(o):
    """
    Returns the length of an object.

    This function attempts to determine the length of various types of objects:
    - If the object has a `__len__` method, it returns that.
    - If it has a `len` attribute, it returns that.
    - If it has a `fileno` method, it returns the size of the file associated with that file descriptor.
    - If it has a `getvalue` method (like BytesIO), it returns the length of its value.

    Args:
        o (Any): The object whose length is to be determined.

    Returns:
        int or None: The length of the object or None if not applicable.
    """
    if hasattr(o, "__len__"):
        return len(o)
    if hasattr(o, "len"):
        return o.len
    if hasattr(o, "fileno"):
        try:
            fileno = o.fileno()
        except io.UnsupportedOperation:
            pass
        else:
            return os.fstat(fileno).st_size
    if hasattr(o, "getvalue"):
        # e.g. BytesIO, cStringIO.StringI
        return len(o.getvalue())
    return None


epoch_aware = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
epoch_naive = dt.datetime(1970, 1, 1)


def json_encoder(obj: t.Any) -> t.Union[int, str]:
    """
    Custom JSON encoder for handling specific data types.

    This function serializes Python's `Decimal`, `datetime`, and `date` types into JSON-compatible formats:

    - `Decimal` is serialized as a string.
    - `datetime` and `date` are serialized as milliseconds since epoch.

    Args:
        obj (Any): The object to serialize.

    Returns:
        Union[int, str]: The serialized value.

    Raises:
        TypeError: If the object type is not supported.

    https://github.com/ijl/orjson#default
    """
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, dt.datetime):
        if obj.tzinfo is not None:
            delta = obj - epoch_aware
        else:
            delta = obj - epoch_naive
        return int(
            delta.microseconds / 1000.0
            + (delta.seconds + delta.days * 24 * 3600) * 1000.0
        )
    if isinstance(obj, dt.date):
        return calendar.timegm(obj.timetuple()) * 1000
    raise TypeError


def json_dumps(obj: t.Any) -> bytes:
    """
    Serialize an object to JSON format using `orjson`.

    This function utilizes a custom encoder to handle specific data types.

    Args:
        obj (Any): The object to serialize.

    Returns:
        bytes: The serialized JSON bytes.

    References:
        https://github.com/ijl/orjson
    """
    return orjson.dumps(
        obj,
        default=json_encoder,
        option=(
            orjson.OPT_PASSTHROUGH_DATETIME
            | orjson.OPT_NON_STR_KEYS
            | orjson.OPT_SERIALIZE_NUMPY
        ),
    )


class MonkServer:
    """
    Represents a connection to a MonkDB server.

    This class manages HTTP connections to a specified MonkDB server and provides methods for sending requests.

    Attributes:
        pool (urllib3.PoolManager): Connection pool manager for handling requests.

    Args:
        server (str): The URL of the MonkDB server.
        **pool_kw: Additional keyword arguments for connection pooling.

    Methods:
        request(method, path, data=None, stream=False, headers=None, username=None,
                password=None, schema=None, backoff_factor=0, **kwargs):
            Sends an HTTP request to the server.

        close():
            Closes the connection pool.

    """

    def __init__(self, server, **pool_kw):
        socket_options = _get_socket_opts(
            pool_kw.pop("socket_keepalive", False),
            pool_kw.pop("socket_tcp_keepidle", None),
            pool_kw.pop("socket_tcp_keepintvl", None),
            pool_kw.pop("socket_tcp_keepcnt", None),
        )
        self.pool = connection_from_url(
            server,
            socket_options=socket_options,
            **pool_kw,
        )

    def request(
        self,
        method,
        path,
        data=None,
        stream=False,
        headers=None,
        username=None,
        password=None,
        schema=None,
        backoff_factor=0,
        **kwargs,
    ):
        """
      Send an HTTP request to the MonkDB server.

      Args:
          method (str): The HTTP method (e.g., GET, POST).
          path (str): The endpoint path for the request.
          data (Optional[bytes]): The body data to send with the request.
          stream (bool): If True, streams the response content.
          headers (Optional[dict]): Additional headers for the request.
          username (Optional[str]): Username for Basic Authentication.
          password (Optional[str]): Password for Basic Authentication.
          schema (Optional[str]): Default schema for the request.
          backoff_factor (float): Factor for exponential backoff on retries.
          **kwargs: Additional keyword arguments for urllib3's urlopen method.

      Returns:
          urllib3.response.HTTPResponse: The response from the server.

      Raises:
          ValueError: If both username and password are provided without authorization header.
      """
        if headers is None:
            headers = {}
        if "Content-Length" not in headers:
            length = super_len(data)
            if length is not None:
                headers["Content-Length"] = length

        # Authentication credentials
        if username is not None:
            if "Authorization" not in headers and username is not None:
                credentials = username + ":"
                if password is not None:
                    credentials += password
                headers["Authorization"] = "Basic %s" % b64encode(
                    credentials.encode("utf-8")
                ).decode("utf-8")
            if "X-User" not in headers:
                headers["X-User"] = username

        if schema is not None:
            headers["Default-Schema"] = schema
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        kwargs["assert_same_host"] = False
        kwargs["redirect"] = False
        kwargs["retries"] = Retry(read=0, backoff_factor=backoff_factor)
        return self.pool.urlopen(
            method,
            path,
            body=data,
            preload_content=not stream,
            headers=headers,
            **kwargs,
        )

    def close(self):
        """
      Close the connection pool for this server.

      This method should be called when no longer needed to release resources properly.
      """
        self.pool.close()


def _json_from_response(response):
    """
     Deserialize JSON content from an HTTP response.

     Args:
         response (urllib3.response.HTTPResponse): The HTTP response object.

     Returns:
         Any: The deserialized JSON content.

     Raises:
         MonkProgrammingError: If the response contains invalid JSON or content-type errors.
     """
    try:
        return orjson.loads(response.data)
    except ValueError as ex:
        raise MonkProgrammingError(
            "The server has responded with an invalid content-type error '{}':\n{}".format(
                response.headers.get("content-type", "unknown"),
                response.data.decode("utf-8"),
            )
        ) from ex


def _blob_path(table, digest):
    """
     Construct the blob path for accessing blob data in a specified table.

     Args:
         table (str): The name of the table containing blobs.
         digest (str): The unique identifier for the blob.

     Returns:
         str: The constructed blob path URL.
     """
    return "/_blobs/{table}/{digest}".format(table=table, digest=digest)


def _ex_to_message(ex):
    """
     Extracts a message from an exception object.

     Args:
         ex (Exception): The exception object from which to extract a message.

     Returns:
         str: The extracted message from the exception.
     """
    return getattr(ex, "message", None) or str(ex) or repr(ex)


def _raise_for_status(response):
    """
     Raise appropriate exceptions based on HTTP response status codes.

     This function raises `MonkIntegrityError` for DuplicateKeyException errors specifically.

     Args:
         response (urllib3.response.HTTPResponse): The HTTP response object.

     Raises:
         MonkIntegrityError: For DuplicateKeyException errors in response content.
         MonkProgrammingError: For other client and server errors based on status codes.
     """
    try:
        return _raise_for_status_real(response)
    except MonkProgrammingError as ex:
        if "DuplicateKeyException" in ex.message:
            raise MonkIntegrityError(
                ex.message, error_trace=ex.error_trace) from ex
        raise


def _raise_for_status_real(response):
    """
     Ensure that only defined exceptions are raised based on HTTP status codes.

     Args:
         response (urllib3.response.HTTPResponse): The HTTP response object.

     Raises:
         MonkConnectionError: For service unavailable errors (503).
         MonkProgrammingError: For client and server errors based on status codes and content type.
     """
    message = ""
    if 400 <= response.status < 500:
        message = "%s Error from Client: %s" % (
            response.status, response.reason)
    elif 500 <= response.status < 600:
        message = "%s Error from Server: %s" % (
            response.status, response.reason)
    else:
        return
    if response.status == 503:
        raise MonkConnectionError(message)
    if response.headers.get("content-type", "").startswith("application/json"):
        data = orjson.loads(response.data)
        error = data.get("error", {})
        error_trace = data.get("error_trace", None)
        if "results" in data:
            errors = [
                res["error_message"]
                for res in data["results"]
                if res.get("error_message")
            ]
            if errors:
                raise MonkProgrammingError("\n".join(errors))
        if isinstance(error, dict):
            raise MonkProgrammingError(
                error.get("message", ""), error_trace=error_trace
            )
        raise MonkProgrammingError(error, error_trace=error_trace)
    raise MonkProgrammingError(message)


def _server_url(server):
    """
   Normalize a given server string into a valid URL format.

   Args:
       server (str): The server string to normalize.

   Returns:
       str: A normalized URL string representing the server.

   Examples:

       >>> print(_server_url('a'))
       http://a

       >>> print(_server_url('a:9345'))
       http://a:9345

       >>> print(_server_url('https://a'))
       https://a

       >>> print(_server_url('demo.monkdb.com'))
       http://demo.monkdb.com
   """
    if not _HTTP_PAT.match(server):
        server = "http://%s" % server
    parsed = urlparse(server)
    url = "%s://%s" % (parsed.scheme, parsed.netloc)
    return url


def _to_server_list(servers):
    """
   Convert a string of servers into a list of normalized URLs.

   Args:
       servers (str | list): A space-separated string of servers or a list of servers.

   Returns:
       list[str]: A list of normalized server URLs.
   """
    if isinstance(servers, str):
        servers = servers.split()
    return [_server_url(s) for s in servers]


def _pool_kw_args(
    verify_ssl_cert,
    ca_cert,
    client_cert,
    client_key,
    timeout=None,
    pool_size=None,
):
    ca_cert = ca_cert or os.environ.get("REQUESTS_CA_BUNDLE", None)
    if ca_cert and not os.path.exists(ca_cert):
        # Sanity check
        raise IOError(
            'The requested CA bundle file "{}" does not exist.'.format(ca_cert))

    kw = {
        "ca_certs": ca_cert,
        "cert_reqs": ssl.CERT_REQUIRED if verify_ssl_cert else ssl.CERT_NONE,
        "cert_file": client_cert,
        "key_file": client_key,
    }
    if timeout is not None:
        if isinstance(timeout, str):
            timeout = float(timeout)
        kw["timeout"] = timeout
    if pool_size is not None:
        kw["maxsize"] = int(pool_size)
    return kw


def _remove_certs_for_non_https(server, kwargs):
    """ 
  Remove SSL certificate arguments from kwargs when using non-HTTPS protocols. 

  Args : 
      server(str) : Server URL 
      kwargs(dict) : Keyword arguments containing SSL settings 

  Returns : 
      dict : Updated kwargs without SSL settings when using non-HTTPS 
  """
    if server.lower().startswith("https"):
        return kwargs
    used_ssl_args = SSL_ONLY_ARGUMENTS & set(kwargs.keys())
    if used_ssl_args:
        kwargs = kwargs.copy()
        for arg in used_ssl_args:
            kwargs.pop(arg)
    return kwargs


def _update_pool_kwargs_for_ssl_minimum_version(server, kwargs):
    """ 
        Update connection pooling settings to allow minimum SSL version support. 

        Args : 
            server(str) : Server URL 
            kwargs(dict) : Keyword arguments containing SSL settings 

        Updates kwargs with minimum supported version for TLS when using HTTPS protocol.
        https://urllib3.readthedocs.io/en/latest/v2-migration-guide.html#https-requires-tls-1-2 
    """
    if Version(urllib3.__version__) >= Version("2"):
        from urllib3.util import parse_url

        scheme, _, host, port, *_ = parse_url(server)
        if scheme == "https":
            kwargs["ssl_minimum_version"] = ssl.TLSVersion.MINIMUM_SUPPORTED


def _create_sql_payload(stmt, args, bulk_args) -> bytes:
    """ 
        Create SQL payload for sending SQL statements. 

        Args : 
            stmt(str) : SQL statement as string. 
            args(Optional[list]) : List of parameters for SQL statement. 
            bulk_args(Optional[list]) : List of bulk parameters. 

        Returns : 
            bytes : Serialized SQL payload as bytes. 

        Raises ValueError when both args and bulk_args are provided.  
    """
    if not isinstance(stmt, str):
        raise ValueError("stmt is not a string")
    if args and bulk_args:
        raise ValueError("Cannot provide both: args and bulk_args")

    data = {"stmt": stmt}
    if args:
        data["args"] = args
    if bulk_args:
        data["bulk_args"] = bulk_args
    return json_dumps(data)


def _get_socket_opts(
    keepalive=True, tcp_keepidle=None, tcp_keepintvl=None, tcp_keepcnt=None
):
    """ 
        Return optional socket options for connection pooling settings. 

        Args : 
            keepalive(bool) : Flag indicating whether TCP keepalive should be enabled. 
            tcp_keepidle(Optional[int]) : Idle time before sending keepalive probes. 
            tcp_keepintvl(Optional[int]) : Interval between keepalive probes. 
            tcp_keepcnt(Optional[int]) : Number of unacknowledged probes before considering connection dead. 

        Returns : 
            list : List of socket options compatible with urllib3's HTTPConnection constructor. 

        Always enables TCP keepalive by default.  
    """
    if not keepalive:
        return None

    # always use TCP keepalive
    opts = [(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)]

    # hasattr check because some options depend on system capabilities
    # see https://docs.python.org/3/library/socket.html#socket.SOMAXCONN
    if hasattr(socket, "TCP_KEEPIDLE") and tcp_keepidle is not None:
        opts.append((socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, tcp_keepidle))
    if hasattr(socket, "TCP_KEEPINTVL") and tcp_keepintvl is not None:
        opts.append((socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, tcp_keepintvl))
    if hasattr(socket, "TCP_KEEPCNT") and tcp_keepcnt is not None:
        opts.append((socket.IPPROTO_TCP, socket.TCP_KEEPCNT, tcp_keepcnt))

    # additionally use urllib3's default socket options
    return list(HTTPConnection.default_socket_options) + opts


class MonkClient:
    """
    MonkDB connection client using MonkDB's HTTP API.
    """

    SQL_PATH = "/_sql?types=true"
    """MonkDB URI path for issuing SQL statements."""

    retry_interval = 30
    """Retry interval for failed servers in seconds."""

    default_server = "http://127.0.0.1:4200"
    """Default server to use if no servers are given on instantiation."""

    def __init__(
        self,
        servers=None,
        timeout=None,
        backoff_factor=0,
        verify_ssl_cert=True,
        ca_cert=None,
        error_trace=False,
        cert_file=None,
        key_file=None,
        ssl_relax_minimum_version=False,
        username=None,
        password=None,
        schema=None,
        pool_size=None,
        socket_keepalive=True,
        socket_tcp_keepidle=None,
        socket_tcp_keepintvl=None,
        socket_tcp_keepcnt=None,
    ):
        if not servers:
            servers = [self.default_server]
        else:
            servers = _to_server_list(servers)

        # Try to derive credentials from first server argument if not
        # explicitly given.
        if servers and not username:
            try:
                url = urlparse(servers[0])
                if url.username is not None:
                    username = url.username
                if url.password is not None:
                    password = url.password
            except Exception as ex:
                logger.warning(
                    "The client is not able to decode credentials from database "
                    "URI. Hence, the client is going to connect to the MonkDB instance without "
                    "authentication: {ex}".format(ex=ex)
                )

        self._active_servers = servers
        self._inactive_servers = []
        pool_kw = _pool_kw_args(
            verify_ssl_cert,
            ca_cert,
            cert_file,
            key_file,
            timeout,
            pool_size,
        )
        pool_kw.update(
            {
                "socket_keepalive": socket_keepalive,
                "socket_tcp_keepidle": socket_tcp_keepidle,
                "socket_tcp_keepintvl": socket_tcp_keepintvl,
                "socket_tcp_keepcnt": socket_tcp_keepcnt,
            }
        )
        self.ssl_relax_minimum_version = ssl_relax_minimum_version
        self.backoff_factor = backoff_factor
        self.server_pool = {}
        self._update_server_pool(servers, **pool_kw)
        self._pool_kw = pool_kw
        self._lock = threading.RLock()
        self._local = threading.local()
        self.username = username
        self.password = password
        self.schema = schema

        self.path = self.SQL_PATH
        if error_trace:
            self.path += "&error_trace=true"

    def close(self):
        for server in self.server_pool.values():
            server.close()

    def _create_server(self, server, **pool_kw):
        kwargs = _remove_certs_for_non_https(server, pool_kw)
        # After updating to urllib3 v2, optionally retain support
        # for TLS 1.0 and TLS 1.1, in order to support connectivity
        # to older versions of CrateDB.
        if self.ssl_relax_minimum_version:
            _update_pool_kwargs_for_ssl_minimum_version(server, kwargs)
        self.server_pool[server] = MonkServer(server, **kwargs)

    def _update_server_pool(self, servers, **pool_kw):
        for server in servers:
            self._create_server(server, **pool_kw)

    def sql(self, stmt, parameters=None, bulk_parameters=None):
        """
        Execute SQL stmt against the monkdb server.
        """
        if stmt is None:
            return None

        data = _create_sql_payload(stmt, parameters, bulk_parameters)
        logger.debug("Sending request to %s with payload: %s", self.path, data)
        content = self._json_request("POST", self.path, data=data)
        logger.debug("JSON response for stmt(%s): %s", stmt, content)

        return content

    def server_infos(self, server):
        response = self._request("GET", "/", server=server)
        _raise_for_status(response)
        content = _json_from_response(response)
        node_name = content.get("name")
        node_version = content.get("version", {}).get("number", "0.0.0")
        return server, node_name, node_version

    def blob_put(self, table, digest, data) -> bool:
        """
        Stores the contents of the file like @data object in a blob under the
        given table and digest.
        """
        response = self._request("PUT", _blob_path(table, digest), data=data)
        if response.status == 201:
            # blob created
            return True
        if response.status == 409:
            # blob exists
            return False
        if response.status in (400, 404):
            raise MonkBlobLocationNotFoundException(table, digest)
        _raise_for_status(response)
        return False

    def blob_del(self, table, digest) -> bool:
        """
        Deletes the blob with given digest under the given table.
        """
        response = self._request("DELETE", _blob_path(table, digest))
        if response.status == 204:
            return True
        if response.status == 404:
            return False
        _raise_for_status(response)
        return False

    def blob_get(self, table, digest, chunk_size=1024 * 128):
        """
        Returns a file like object representing the contents of the blob
        with the given digest.
        """
        response = self._request("GET", _blob_path(table, digest), stream=True)
        if response.status == 404:
            raise MonkDigestNotFoundException(table, digest)
        _raise_for_status(response)
        return response.stream(amt=chunk_size)

    def blob_exists(self, table, digest) -> bool:
        """
        Returns true if the blob with the given digest exists
        under the given table.
        """
        response = self._request("HEAD", _blob_path(table, digest))
        if response.status == 200:
            return True
        elif response.status == 404:
            return False
        _raise_for_status(response)
        return False

    def _add_server(self, server):
        with self._lock:
            if server not in self.server_pool:
                self._create_server(server, **self._pool_kw)

    def _request(self, method, path, server=None, **kwargs):
        """Execute a request to the cluster

        A server is selected from the server pool.
        """
        while True:
            next_server = server or self._get_server()
            try:
                response = self.server_pool[next_server].request(
                    method,
                    path,
                    username=self.username,
                    password=self.password,
                    backoff_factor=self.backoff_factor,
                    schema=self.schema,
                    **kwargs,
                )
                redirect_location = response.get_redirect_location()
                if redirect_location and 300 <= response.status <= 308:
                    redirect_server = _server_url(redirect_location)
                    self._add_server(redirect_server)
                    return self._request(
                        method, path, server=redirect_server, **kwargs
                    )
                if not server and response.status in SERVICE_UNAVAILABLE_STATUSES:
                    with self._lock:
                        # drop server from active ones
                        self._drop_server(next_server, response.reason)
                else:
                    return response
            except (
                MaxRetryError,
                ReadTimeoutError,
                SSLError,
                HTTPError,
                ProxyError,
            ) as ex:
                ex_message = _ex_to_message(ex)
                if server:
                    raise MonkConnectionError(
                        "The requested server unavailable: %s" % ex_message
                    ) from ex
                preserve_server = False
                if isinstance(ex, ProtocolError):
                    preserve_server = any(
                        t in [type(arg) for arg in ex.args]
                        for t in PRESERVE_ACTIVE_SERVER_EXCEPTIONS
                    )
                if not preserve_server:
                    with self._lock:
                        # drop server from active ones
                        self._drop_server(next_server, ex_message)
            except Exception as e:
                raise MonkProgrammingError(_ex_to_message(e)) from e

    def _json_request(self, method, path, data):
        """
        Issue request against the monkdb HTTP API.
        """

        response = self._request(method, path, data=data)
        _raise_for_status(response)
        if len(response.data) > 0:
            return _json_from_response(response)
        return response.data

    def _get_server(self):
        """
        Get server to use for request.
        Also process inactive server list, re-add them after given interval.
        """
        with self._lock:
            inactive_server_count = len(self._inactive_servers)
            for _ in range(inactive_server_count):
                try:
                    ts, server, message = heapq.heappop(self._inactive_servers)
                except IndexError:
                    pass
                else:
                    if (ts + self.retry_interval) > time():
                        # Not yet, put it back
                        heapq.heappush(
                            self._inactive_servers, (ts, server, message)
                        )
                    else:
                        self._active_servers.append(server)
                        logger.warning(
                            "Restored server %s into active pool", server
                        )

            # if none is old enough, use oldest
            if not self._active_servers:
                ts, server, message = heapq.heappop(self._inactive_servers)
                self._active_servers.append(server)
                logger.info("Restored server %s into active pool", server)

            server = self._active_servers[0]
            self._roundrobin()

            return server

    @property
    def active_servers(self):
        """get the active servers for this client"""
        with self._lock:
            return list(self._active_servers)

    def _drop_server(self, server, message):
        """
        Drop server from active list and adds it to the inactive ones.
        """
        try:
            self._active_servers.remove(server)
        except ValueError:
            pass
        else:
            heapq.heappush(self._inactive_servers, (time(), server, message))
            logger.warning(
                "The client has removed the requested server %s from MonkDB's active pool of servers", server)

        # if this is the last server raise exception, otherwise try next
        if not self._active_servers:
            raise MonkConnectionError(
                ("No more servers are available, and the exception from last server is: %s")
                % message
            )

    def _roundrobin(self):
        """
        Very simple round-robin implementation
        """
        self._active_servers.append(self._active_servers.pop(0))

    def __repr__(self):
        return "<Client {0}>".format(str(self._active_servers))

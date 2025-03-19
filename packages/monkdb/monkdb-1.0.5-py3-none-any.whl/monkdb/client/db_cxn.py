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

from verlib2 import Version

from .objects import MonkBlobstoreContainer
from .db_cursor import MonkCursor
from .exceptions import MonkConnectionError, MonkProgrammingError
from .http_connections import MonkClient


class MonkConnection:
    """
    Represents a connection to a MonkDB database.

    This class manages the connection to one or more MonkDB servers, handling
    connection pooling, SSL configuration, authentication, and other connection-related
    settings. It provides methods for creating cursors, closing the connection,
    and accessing blob containers.

    .. note::
        Transactions are not supported in MonkDB. The `commit` method is present
        for compatibility but does not perform any actual transaction operations.
    """

    def __init__(
        self,
        servers=None,
        timeout=None,
        backoff_factor=0,
        client=None,
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
        converter=None,
        time_zone=None,
    ):
        """
        Initializes a new MonkConnection instance.

        :param servers:
            It is either a string in the form of '<hostname>:<port>' or a list of servers
            in the form of ['<hostname>:<port>', '...']. Specifies the MonkDB
            server(s) to connect to.
        :type servers: str or list[str], optional
        :param timeout:
            It defines the retry timeout for in case MonkDB servers are unreachable (in seconds).
        :type timeout: int, optional
        :param backoff_factor:
            It defines the retry interval for the servers that are unreachable (in seconds).
        :type backoff_factor: float, optional
        :param client:
            MonkClient used to communicate with MonkDB (for testing purposes).
        :type client: MonkClient, optional
        :param verify_ssl_cert:
            If it is set to ``False``, it disables SSL server certificate verification.
            Defaults to ``True``.
        :type verify_ssl_cert: bool, optional
        :param ca_cert:
            Mentions a path to a CA certificate to use when verifying the SSL server
            certificate.
        :type ca_cert: str, optional
        :param error_trace:
            If it is set to ``True``, it returns a whole stacktrace of any server error if
            one occurs.
        :type error_trace: bool, optional
        :param cert_file:
            It is a path to the client certificate that a client connection must present to the server.
        :type cert_file: str, optional
        :param key_file:
            It is a path to the client key to use when communicating with the server.
        :type key_file: str, optional
        :param username:
            The username provisioned in the database.
        :type username: str, optional
        :param password:
            The password of the provisioned user in the database.
        :type password: str, optional
        :param schema:
            The schema to leverage for connection connection.
        :type schema: str, optional
        :param pool_size:
            The number of connections to save which can be reused. More than 1 is
            useful in multithreaded situations.
        :type pool_size: int, optional
        :param socket_keepalive:
            Allows enabling TCP keepalive on socket level. It defaults to ``True``.
        :type socket_keepalive: bool, optional
        :param socket_tcp_keepidle:
            It sets the ``TCP_KEEPIDLE`` socket option, which overrides
            ``net.ipv4.tcp_keepalive_time`` kernel setting if ``socket_keepalive``
            is ``True``.
        :type socket_tcp_keepidle: int, optional
        :param socket_tcp_keepintvl:
            It sets the ``TCP_KEEPINTVL`` socket option, that overrides
            ``net.ipv4.tcp_keepalive_intvl`` kernel setting if ``socket_keepalive``
            is ``True``.
        :type socket_tcp_keepintvl: int, optional
        :param socket_tcp_keepcnt:
            It sets the ``TCP_KEEPCNT`` socket option, which overrides
            ``net.ipv4.tcp_keepalive_probes`` kernel setting if ``socket_keepalive``
            is ``True``.
        :type socket_tcp_keepcnt: int, optional
        :param converter:
            It is a `Converter` object to propagate to newly created `MonkCursor` objects.
        :type converter: object, optional
        :param time_zone:
            It is a time zone specifier used for returning `TIMESTAMP` types as
            timezone-aware native Python `datetime` objects.

            Different data types are supported. Available options are:

            - ``datetime.timezone.utc``
            - ``datetime.timezone(datetime.timedelta(hours=7), name="MST")``
            - ``pytz.timezone("Australia/Sydney")``
            - ``zoneinfo.ZoneInfo("Australia/Sydney")``
            - ``+0530`` (UTC offset in string format)

            The driver always returns timezone-"aware" `datetime` objects,
            with their `tzinfo` attribute set.

            When `time_zone` is `None`, the returned `datetime` objects are
            using Coordinated Universal Time (UTC), because MonkDB is storing
            timestamp values in this format.

            When `time_zone` is given, the timestamp values will be transparently
            converted from UTC to use the given time zone.
        :type time_zone: object, optional

        :raises MonkConnectionError: If a connection to the server cannot be established.
        """  # noqa: E501

        self._converter = converter
        self.time_zone = time_zone

        if client:
            self.client = client
        else:
            self.client = MonkClient(
                servers,
                timeout=timeout,
                backoff_factor=backoff_factor,
                verify_ssl_cert=verify_ssl_cert,
                ca_cert=ca_cert,
                error_trace=error_trace,
                cert_file=cert_file,
                key_file=key_file,
                ssl_relax_minimum_version=ssl_relax_minimum_version,
                username=username,
                password=password,
                schema=schema,
                pool_size=pool_size,
                socket_keepalive=socket_keepalive,
                socket_tcp_keepidle=socket_tcp_keepidle,
                socket_tcp_keepintvl=socket_tcp_keepintvl,
                socket_tcp_keepcnt=socket_tcp_keepcnt,
            )
        self.lowest_server_version = self._lowest_server_version()
        self._closed = False

    def cursor(self, **kwargs) -> MonkCursor:
        """
        Return a new Cursor Object using the connection.

        :param kwargs:
            Optional keyword arguments to configure the cursor.

        :keyword converter:
            A `Converter` object to use for the cursor, overriding the
            connection's default converter.
        :type converter: object, optional
        :keyword time_zone:
            A time zone specifier to use for the cursor, overriding the
            connection's default time zone.
        :type time_zone: object, optional

        :return: A new `MonkCursor` object associated with this connection.
        :rtype: MonkCursor

        :raises MonkProgrammingError: If the connection is closed.
        """
        converter = kwargs.pop("converter", self._converter)
        time_zone = kwargs.pop("time_zone", self.time_zone)
        if not self._closed:
            return MonkCursor(
                connection=self,
                converter=converter,
                time_zone=time_zone,
            )
        else:
            raise MonkProgrammingError("Connection closed")

    def close(self):
        """
        Close the connection now.

        This method closes the underlying client connection and marks the
        `MonkConnection` as closed, preventing further operations.
        """
        self._closed = True
        self.client.close()

    def commit(self):
        """
        Transactions are not supported, so `commits` is not implemented.

        :raises MonkProgrammingError: If the connection is closed.
        """
        if self._closed:
            raise MonkProgrammingError("Connection closed")

    def get_blob_container(self, container_name):
        """Retrieve a BlobContainer for `container_name`.

        :param container_name: the name of the BLOB container.
        :type container_name: str
        :return: a :class:`MonkBlobstoreContainer` object representing the blob container.
        :rtype: MonkBlobstoreContainer
        """
        return MonkBlobstoreContainer(container_name, self)

    def _lowest_server_version(self):
        """
        Determines the lowest server version among all active servers.

        This method iterates through the active servers in the client and
        retrieves their versions. It then returns the lowest version found.

        :return: The lowest server version as a `Version` object.
                 Returns Version("0.0.0") if no server versions are found.
        :rtype: verlib2.Version
        """
        lowest = None
        for server in self.client.active_servers:
            try:
                _, _, version = self.client.server_infos(server)
                version = Version(version)
            except (ValueError, ConnectionError):
                continue
            if not lowest or version < lowest:
                lowest = version
        return lowest or Version("0.0.0")

    def __repr__(self):
        """
        Return a string representation of the connection.
        """
        return "<Connection {0}>".format(repr(self.client))

    def __enter__(self):
        """
        Enter method for context management.
        """
        return self

    def __exit__(self, *excs):
        """
        Exit method for context management.  Closes the connection.
        """
        self.close()


# For backwards compatibility and not to break existing imports
"""Alias for MonkConnection for backwards compatibility."""
connect = MonkConnection

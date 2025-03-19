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

class MonkError(Exception):
    """
    Base class for exceptions in the MonkDB.

    This custom exception class is used for general errors in the MonkDB, and it allows for 
    additional error stack trace information.

    Attributes:
        message (str): A descriptive message explaining the error.
        error_trace (str): Optional stack trace for debugging the error.

    Methods:
        __str__(): Returns a string representation of the error, including the message and stack trace (if provided).
    """

    def __init__(self, message=None, error_trace=None):
        if message:
            self.message = message
        super(MonkError, self).__init__(message)
        self.error_trace = error_trace

    def __str__(self):
        if self.error_trace is None:
            return super().__str__()
        return "\n".join([super().__str__(), str(self.error_trace)])


class MonkWarning(Exception):
    """
    Custom warning class for the MonkDB.

    This class is used to indicate potential issues that are not critical errors. It is a subclass 
    of the built-in Exception class and does not introduce any new behavior.
    """
    pass


class MonkInterfaceError(MonkError):
    """
    Raised when there is an interface-related error in the MonkDB.

    This is a subclass of MonkError and is used to handle errors related to interface issues.
    """
    pass


class MonkDatabaseError(MonkError):
    """
    Base class for database-related errors in the MonkDB.

    This custom exception class is used for errors related to database operations.
    """
    pass


class MonkInternalError(MonkDatabaseError):
    """
    Raised when there is an internal error within the database in the MonkDB.

    This subclass of MonkDatabaseError is used to handle internal database issues.
    """
    pass


class MonkOperationalError(MonkDatabaseError):
    """
    Raised for operational errors in the MonkDB's system.

    This subclass of MonkDatabaseError is used when there are issues related to the database's 
    operation, such as connection problems or database unavailability.
    """
    pass


class MonkProgrammingError(MonkDatabaseError):
    """
    Raised when there is a programming error in the MonkDB's operations.

    This subclass of MonkDatabaseError indicates issues such as incorrect SQL syntax or invalid queries.
    """
    pass


class MonkIntegrityError(MonkDatabaseError):
    """
    Raised when there is an integrity error in the MonkDB's operations.

    This subclass of MonkDatabaseError handles situations where database integrity constraints (e.g., 
    foreign key, unique constraints) are violated.
    """
    pass


class MonkDataError(MonkDatabaseError):
    """
    Raised for data-related errors in the MonkDB's operations.

    This subclass of MonkDatabaseError is used when there are issues with the data being processed 
    or retrieved from the database.
    """
    pass


class MonkNotSupportedError(MonkDatabaseError):
    """
    Raised when an operation is attempted that is not supported in the MonkDB's system.

    This subclass of MonkDatabaseError is used when an unsupported database feature or operation 
    is requested.
    """
    pass


class MonkConnectionError(MonkOperationalError):
    """
    Raised for connection-related errors in the MonkDB's system.

    This subclass of MonkOperationalError is specifically used to handle connection issues with 
    the database, such as timeout or failed connection.
    """
    pass


class MonkBlobException(Exception):
    """
    Base class for exceptions related to blobs (binary large objects) in MonkDB.

    This class is used for errors related to blob operations (e.g., storing, retrieving, or processing 
    large binary data such as images or files).

    Attributes:
        table (str): The table where the blob is stored.
        digest (str): The unique identifier or hash of the blob.

    Methods:
        __str__(): Returns a string representation of the exception, combining the table and digest information.
    """

    def __init__(self, table, digest):
        self.table = table
        self.digest = digest

    def __str__(self):
        return "{table}/{digest}".format(table=self.table, digest=self.digest)


class MonkDigestNotFoundException(MonkBlobException):
    """
    Raised when a requested blob digest cannot be found in the MonkDB.

    This subclass of MonkBlobException is used when the system is unable to locate a blob 
    based on the provided digest.
    """
    pass


class MonkBlobLocationNotFoundException(MonkBlobException):
    """
    Raised when a blob location cannot be found in the MonkDB.

    This subclass of MonkBlobException is used when the system is unable to determine the location 
    of a blob (e.g., when retrieving a file from a specific location).
    """
    pass


class MonkTimezoneUnawareException(MonkError):
    """
    Raised when timezone information is missing or invalid in the MonkDB.

    This subclass of MonkError is used when a function or operation expects timezone-aware data 
    but receives timezone-unaware data instead.
    """
    pass

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

import hashlib


class MonkBlobstoreContainer:
    """
    Represents a container for managing blobs in MonkDB's blob storage system.

    This class provides methods to upload, download, delete, check existence of blobs, and compute their digests.
    It interacts with the provided connection object to perform these actions in a backend blob storage system.

    Attributes:
        container_name (str): The name of the container in the blob store.
        connection (object): The connection object used to interact with the backend blob storage.
    """

    def __init__(self, container_name, connection):
        """
        Initializes a MonkBlobstoreContainer instance.

        :param container_name: The name of the container in the blob store.
        :param connection: The connection object used to interact with the blob storage system.
        """
        self.container_name = container_name
        self.connection = connection

    def _compute_digest(self, file):
        """
        Computes the SHA-1 digest of the given file.

        This method reads the file in chunks, computes its SHA-1 hash, and returns the hex representation of the digest.

        :param file: The file object whose digest is to be computed. Must support the `.read()` and `.seek()` methods.
        :return: A string representing the SHA-1 hex digest of the file.
        """
        file.seek(0)
        m = hashlib.sha1()  # noqa: S324
        while True:
            dgst = file.read(1024 * 32)
            if not dgst:
                break
            m.update(dgst)
        file.seek(0)
        return m.hexdigest()

    def put(self, file, digest=None):
        """
        Uploads a blob (file) to the container.

        If a digest is provided, it will be used as the identifier for the file in the blob storage.
        If no digest is provided, it is computed using the `_compute_digest` method.

        :param file: The file object to be uploaded. The file must support `.read()` and `.seek()` methods.
        :param digest: (Optional) The SHA-1 digest of the file contents. If not provided, it will be computed.
        :return: If digest is provided, returns a boolean indicating whether the blob was newly created. 
                 Otherwise, it returns the computed hex digest of the file.
        """
        if digest:
            actual_digest = digest
        else:
            actual_digest = self._compute_digest(file)

        created = self.connection.client.blob_put(
            self.container_name, actual_digest, file)

        if digest:
            return created
        return actual_digest

    def get(self, digest, chunk_size=1024 * 128):
        """
        Retrieves the contents of a blob from the container.

        :param digest: The SHA-1 hex digest of the blob to be retrieved.
        :param chunk_size: The size (in bytes) of the chunks to be returned in each iteration (default is 128KB).
        :return: A generator that yields chunks of data from the blob.
        """
        return self.connection.client.blob_get(
            self.container_name, digest, chunk_size
        )

    def delete(self, digest):
        """
        Deletes a blob from the container.

        :param digest: The SHA-1 hex digest of the blob to be deleted.
        :return: True if the blob existed and was deleted, otherwise False.
        """
        return self.connection.client.blob_del(self.container_name, digest)

    def exists(self, digest):
        """
        Checks if a blob exists in the container.

        :param digest: The SHA-1 hex digest of the blob to check.
        :return: True if the blob exists, otherwise False.
        """
        return self.connection.client.blob_exists(self.container_name, digest)

    def __repr__(self):
        """
        Returns a string representation of the MonkBlobstoreContainer instance.

        :return: A string representing the container, e.g., "<BlobContainer 'container_name'>".
        """
        return "<BlobContainer '{0}'>".format(self.container_name)

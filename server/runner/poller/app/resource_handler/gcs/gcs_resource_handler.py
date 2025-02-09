# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import structlog
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import storage  # type: ignore[attr-defined]
from google.cloud.exceptions import GoogleCloudError
from google.cloud.storage.client import Client as GCSClient

from poller.app.app_location_parser.app_location_parser import AppLocation
from poller.app.resource_handler.resource_handler import ResourceHandler

logger = structlog.getLogger(__name__)


class GCSResourceHandler(ResourceHandler):
    def __init__(self, app_location: AppLocation, client: GCSClient | None = None) -> None:
        super().__init__(app_location)
        self.client = client or self.initialize_gcs_client()

    def initialize_gcs_client(self) -> GCSClient:
        """
        Initialize the GCS client, with fallback to credentials file if necessary.
        """
        try:
            # First, try to create a GCS client without explicit credentials
            client = storage.Client()
            client.get_bucket(self.app_location.bucket)  # Test access
        except (GoogleCloudError, DefaultCredentialsError):
            # If the first method fails, try to use credentials from a JSON file
            try:
                return storage.Client.from_service_account_json(
                    json_credentials_path=self.poller_config.gcp_credentials,
                )
            except FileNotFoundError as e:
                msg = "Could not find GCP credentials file and no service account available."
                raise FileNotFoundError(msg) from e
        else:
            return client

    def poll(self) -> None:
        bucket_name = self.get_bucket()
        bucket = self.client.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=self.app_location.path)
        notification_needed = False
        for blob in blobs:
            file_name = os.path.basename(blob)
            if file_name not in self.poller_config.allowed_files:
                logger.debug("skipped file", filename=file_name, allowed_files=self.poller_config.allowed_files)
                continue
            if self.is_object_outdated(blob.updated, blob.name):
                self.download_file(bucket_name, blob.name, self.get_destination_path(file_name))
                notification_needed = True

            if notification_needed:
                self.notify_executor()

    def _download_file(self, bucket_name: str | None, object_name: str, download_path: str) -> None:
        bucket = self.client.get_bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.download_to_filename(download_path)

# Proprietary Changes made for Trainy under the Trainy Software License
# Original source: skypilot: https://github.com/skypilot-org/skypilot
# which is Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cloud object stores.

Currently, used for transferring data in bulk.  Thus, this module does not
offer file-level calls (e.g., open, reading, writing).

TODO:
* Better interface.
* Better implementation (e.g., fsspec, smart_open, using each cloud's SDK).
"""

import subprocess
import typing

from konduktor import logging
from konduktor.data import data_utils, gcp, storage_utils

logger = logging.get_logger(__name__)

# TODO(asaiacai): this internal API is shit and should just be unified with
# the storage_utils.AbstractStore class. Shit Berkeley EECS as usual.


class CloudStorage:
    """Interface for a cloud object store."""

    # this needs to be overridden by the subclass
    _STORE: typing.Type[storage_utils.AbstractStore]

    def is_directory(self, url: str) -> bool:
        """Returns whether 'url' is a directory.

        In cloud object stores, a "directory" refers to a regular object whose
        name is a prefix of other objects.
        """
        raise NotImplementedError

    def make_sync_dir_command(self, source: str, destination: str) -> str:
        """Makes a runnable bash command to sync a 'directory'."""
        raise NotImplementedError

    def make_sync_file_command(self, source: str, destination: str) -> str:
        """Makes a runnable bash command to sync a file."""
        raise NotImplementedError

    def check_credentials(self):
        """Checks if the user has access credentials to this cloud."""
        return self._STORE.check_credentials()

    def check_credentials_from_secret(self):
        """Checks if the user has access credentials to this cloud."""
        return self._STORE.check_credentials_from_secret()

    def set_secret_credentials(self):
        """Set the credentials from the secret"""
        return self._STORE.set_secret_credentials()


class GcsCloudStorage(CloudStorage):
    """Google Cloud Storage."""

    # We use gsutil as a basic implementation.  One pro is that its -m
    # multi-threaded download is nice, which frees us from implementing
    # parellel workers on our end.
    # The gsutil command is part of the Google Cloud SDK, and we reuse
    # the installation logic here.
    _INSTALL_GSUTIL = gcp.GOOGLE_SDK_INSTALLATION_COMMAND
    _STORE: typing.Type[storage_utils.AbstractStore] = gcp.GcsStore

    @property
    def _gsutil_command(self):
        gsutil_alias, alias_gen = data_utils.get_gsutil_command()
        return (
            f'{alias_gen}; GOOGLE_APPLICATION_CREDENTIALS='
            f'{gcp.DEFAULT_GCP_APPLICATION_CREDENTIAL_PATH}; '
            # Explicitly activate service account. Unlike the gcp packages
            # and other GCP commands, gsutil does not automatically pick up
            # the default credential keys when it is a service account.
            'gcloud auth activate-service-account '
            '--key-file=$GOOGLE_APPLICATION_CREDENTIALS '
            '2> /dev/null || true; '
            f'{gsutil_alias}'
        )

    def is_directory(self, url: str) -> bool:
        """Returns whether 'url' is a directory.
        In cloud object stores, a "directory" refers to a regular object whose
        name is a prefix of other objects.
        """
        commands = [self._INSTALL_GSUTIL]
        commands.append(f'{self._gsutil_command} ls -d {url}')
        command = ' && '.join(commands)
        p = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            shell=True,
            check=True,
            executable='/bin/bash',
        )
        out = p.stdout.decode().strip()
        # Edge Case: Gcloud command is run for first time #437
        out = out.split('\n')[-1]
        # If <url> is a bucket root, then we only need `gsutil` to succeed
        # to make sure the bucket exists. It is already a directory.
        _, key = data_utils.split_gcs_path(url)
        if not key:
            return True
        # Otherwise, gsutil ls -d url will return:
        #   --> url.rstrip('/')          if url is not a directory
        #   --> url with an ending '/'   if url is a directory
        if not out.endswith('/'):
            assert out == url.rstrip('/'), (out, url)
            return False
        url = url if url.endswith('/') else (url + '/')
        assert out == url, (out, url)
        return True

    def make_sync_dir_command(self, source: str, destination: str) -> str:
        """Downloads a directory using gsutil."""
        download_via_gsutil = (
            f'{self._gsutil_command} ' f'rsync -e -r {source} {destination}'
        )
        all_commands = [self._INSTALL_GSUTIL]
        all_commands.append(download_via_gsutil)
        return ' && '.join(all_commands)

    def make_sync_file_command(self, source: str, destination: str) -> str:
        """Downloads a file using gsutil."""
        download_via_gsutil = f'{self._gsutil_command} ' f'cp {source} {destination}'
        all_commands = [self._INSTALL_GSUTIL]
        all_commands.append(download_via_gsutil)
        return ' && '.join(all_commands)


# Maps bucket's URIs prefix(scheme) to its corresponding storage class
_REGISTRY = {
    'gs': GcsCloudStorage(),
    # TODO(asaiacai): Add other cloud stores here
    # 's3': S3CloudStorage(),
    # 'r2': R2CloudStorage(),
    # 'cos': IBMCosCloudStorage(),
    # 'oci': OciCloudStorage(),
    # # TODO: This is a hack, as Azure URL starts with https://, we should
    # # refactor the registry to be able to take regex, so that Azure blob can
    # # be identified with `https://(.*?)\.blob\.core\.windows\.net`
    # 'https': AzureBlobCloudStorage()
}

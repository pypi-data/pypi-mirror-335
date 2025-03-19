from typing import Any, Union

Path = str
SourceType = Union[Path]
StorageHandle = Any

# TODO(asaiacai) This should match the cloud store
# classes in cloud_stores.py,
# should honestly just use one or the other instead of both
STORE_ENABLED_CLOUDS = ['gs']

_STORAGE_LOG_FILE_NAME = 'storage.log'

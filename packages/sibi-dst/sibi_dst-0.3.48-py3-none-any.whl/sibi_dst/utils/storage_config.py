from .storage_manager import StorageManager
from .credentials import ConfigManager

class StorageConfig:
    def __init__(self, config:ConfigManager, depots:dict):
        self.conf = config
        self.depots = depots
        self._initialize_storage()
        self.storage_manager = StorageManager(self.base_storage, self.filesystem_type, self.filesystem_options)
        self.depot_paths, self.depot_names = self.storage_manager.rebuild_depot_paths(depots)

    def _initialize_storage(self):
        self.filesystem_type = self.conf.get('fs_type','file')
        self.base_storage = self.conf.get('fs_path', "local_storage/")
        if self.filesystem_type == "file":
            self.filesystem_options ={}
        else:
            self.filesystem_options = {
                "key": self.conf.get('fs_key',''),
                "secret": self.conf.get('fs_secret'),
                "token": self.conf.get('fs_token'),
                "skip_instance_cache":True,
                "use_listings_cache": False,
                "client_kwargs": {
                    "endpoint_url": self.conf.get('fs_endpoint')
                }
            }
            self.filesystem_options = {k: v for k, v in self.filesystem_options.items() if v}
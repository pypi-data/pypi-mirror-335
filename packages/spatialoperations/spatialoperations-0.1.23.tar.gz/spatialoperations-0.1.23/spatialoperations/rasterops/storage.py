import zarr
from pathlib import Path
import s3fs
import os
import logging
import json
import numpy as np

class BaseStorage:
    def __init__(self):
        pass

    def get_storage(self):
        pass

    def get_root_group(self):
        pass

    def create_dataset(self, shape, group=None, varnames=None):
        pass


class ArrayLakeStorage(BaseStorage):
    def __init__(self, client: str, repo: str, disk_store: str):
        self.client = client
        self.repo = repo
        self.disk_store = disk_store

    def get_storage(self):
        return self.repo.store

    @property
    def root_group(self):
        return self.repo.root_group

    def create_group(self, group: str):
        self.root_group.create_group(group)

    def get_group(self, group: str = None):
        return self.root_group[group]

    def delete_group(self, group: str):
        del self.root_group[group]

    def create_dataset(self, var, group=None, varnames=None):
        pass


class DummyRepo:
    def commit(self, message: str):
        pass


class PlainOlZarrStore(BaseStorage):
    def __getstate__(self):
        """Return state for pickling"""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['store']
        return state

    def __setstate__(self, state):
        """Reconstruct object from pickled state"""
        self.__dict__.update(state)
        self._initialize_store()
    
    def __init__(self, path: str):
        self.path = path  # Save the path for serialization
        self._initialize_store()
        
    def _initialize_store(self):
        """Initialize the store after basic attributes are set"""
        if self.path.startswith('s3://'):
            # Parse S3 URL
            prefix = self.path.replace('s3://', '')
            s3 = s3fs.S3FileSystem(
                key=os.getenv("AWS_ACCESS_KEY_ID"),
                secret=os.getenv("AWS_SECRET_ACCESS_KEY"),
                client_kwargs={'endpoint_url': os.getenv("AWS_ENDPOINT_URL")},
                asynchronous=True,
            )
            
            self.store = zarr.storage.FsspecStore(
                s3,
                path=prefix
            )
            
        else:
            # Fallback to local storage
            self.store = zarr.storage.DirectoryStore(Path(self.path) / "data.zarr")
    
    def save_metadata(self, key: str, values: dict):
        self.root_group.attrs[key] = values
        
    def store_active_idxs(self, var: str, group: str, idxs: list[tuple[int, int]], clear_previous: bool = False):
        if clear_previous:
            logging.info(f"Clearing previous active idxs for {var} in {group}")
            try:
                del self.root_group.attrs["stored_idxs"][f"{group}/{var}"]
            except KeyError:
                pass
        else:
            logging.info(f"Processed {len(idxs)} tiles")
        if "stored_idxs" not in self.root_group.attrs:
            self.root_group.attrs["stored_idxs"] = dict()

        idxs = [i for i in idxs if i is not None]

        if f"{group}/{var}" in self.root_group.attrs["stored_idxs"] and not clear_previous:
            idxs = (
                self.root_group.attrs["stored_idxs"][f"{group}/{var}"]
                + idxs
            )
            idxs = list(set([tuple(i) for i in idxs]))

        self.root_group.attrs["stored_idxs"] = {
            **self.root_group.attrs["stored_idxs"],
            f"{group}/{var}": idxs,
        }
        
    def get_active_idxs(self, var: str, group: str | None = None):
        if group is None:
            return self.root_group.attrs["stored_idxs"][var]
        else:
            return self.root_group.attrs["stored_idxs"][f"{group}/{var}"]
        
    def get_multi_active_idxs(self, vars: list[str], group: str | None = None):
        idx_buffer = []
        for var in vars:
            idx_buffer.extend(self.get_active_idxs(var, group))
        return list(set([tuple(i) for i in idx_buffer]))
    
    def get_storage(self):
        return self.store

    @property
    def root_group(self):
        return zarr.group(store=self.store)

    def create_group(self, group: str = ''):
        self.root_group.create_group(group)

    def get_group(self, group: str = None):
        return self.root_group[group]

    def delete_group(self, group: str):
        del self.root_group[group]

    def create_dataset(self, var, group=None, varnames=None):
        pass


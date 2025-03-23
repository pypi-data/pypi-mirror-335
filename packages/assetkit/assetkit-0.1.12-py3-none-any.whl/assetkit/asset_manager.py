
from importlib.resources import files
import os
from typing import Dict, List


class AssetFile:
    def __init__(self, path_obj):
        self._path = path_obj

    def text(self) -> str:
        return self._path.read_text()

    def bytes(self) -> bytes:
        return self._path.read_bytes()

    def path(self) -> str:
        return str(self._path)

    def __repr__(self):
        return f"<AssetFile path='{self.path()}' size={len(self.bytes())} bytes>"


class AssetManager:
    def __init__(self, package_root: str, resource_dir: str = "resources"):
        self._base = files(package_root) / resource_dir
        self._index = self._build_index()

    def _build_index(self) -> Dict[str, AssetFile]:
        index = {}

        def walk(path_obj, prefix=""):
            for item in path_obj.iterdir():
                rel = os.path.join(prefix, item.name).replace('\\', '/')  # Normalize separators
                if item.is_dir():
                    walk(item, rel)
                else:
                    index[rel] = AssetFile(item)

        walk(self._base)
        return index

    def __getitem__(self, key: str) -> AssetFile:
        if key not in self._index:
            raise KeyError(f"Asset not found: {key}")
        return self._index[key]

    def list(self) -> List[str]:
        return list(self._index.keys())

    def find(self, suffix: str) -> List[str]:
        return [k for k in self._index if k.endswith(suffix)]

    def __contains__(self, key: str) -> bool:
        return key in self._index

    def __repr__(self):
        return f"<AssetManager {len(self._index)} assets>"

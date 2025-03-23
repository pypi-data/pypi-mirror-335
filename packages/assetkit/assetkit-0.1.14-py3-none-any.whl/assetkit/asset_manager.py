import os
from pathlib import Path
from typing import Dict, List


class AssetFile:
    def __init__(self, path_obj: Path):
        self._path = path_obj

    def text(self) -> str:
        return self._path.read_text(encoding="utf-8")

    def bytes(self) -> bytes:
        return self._path.read_bytes()

    def path(self) -> str:
        return str(self._path.resolve())

    def __repr__(self):
        return f"<AssetFile path='{self.path()}' size={len(self.bytes())} bytes>"


class AssetManager:
    def __init__(self, package_root: Path, resource_dir: str = "resources"):
        """
        :param package_root: Path to the root of the installed package (directory containing resources/)
        :param resource_dir: Relative path inside the package where assets are located
        """
        self._base = Path(package_root).resolve() / resource_dir
        if not self._base.exists():
            raise FileNotFoundError(f"AssetManager: Resource directory not found: {self._base}")
        self._index = self._build_index()

    def _build_index(self) -> Dict[str, AssetFile]:
        index = {}

        def walk(path_obj: Path, prefix=""):
            for item in path_obj.iterdir():
                rel = os.path.join(prefix, item.name).replace("\\", "/")  # Normalize for consistency
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

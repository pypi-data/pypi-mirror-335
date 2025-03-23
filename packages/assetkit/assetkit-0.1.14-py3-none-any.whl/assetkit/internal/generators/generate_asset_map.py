from pathlib import Path
from assetkit.asset_manager import AssetManager
import re


def sanitize_key_to_attr(key: str) -> str:
    """
    Convert an asset path like 'config/model.yaml' into a valid Python attribute name like 'config_model_yaml'.
    """
    parts = Path(key).parts
    sanitized = [re.sub(r"[^0-9a-zA-Z_]", "_", part) for part in parts]
    return "_".join(sanitized).strip("_")


def generate_asset_mapping(package_path: Path, resource_dir: str = "resources/assets", output_filename: str = "assets.py"):
    """
    Generate a Python mapping file (e.g., assets.py) with a proxy class to access assets in a Pythonic way.

    Parameters:
    - package_path: Path to the root Python package directory (e.g., Path("my_package/"))
    - resource_dir: Relative path inside the package to the asset directory
    - output_filename: Filename to write the asset mapping to (default: "assets.py")
    """
    package_path = Path(package_path).resolve()
    if not package_path.exists():
        raise FileNotFoundError(f"Package path '{package_path}' does not exist.")

    manager = AssetManager(package_root=package_path, resource_dir=resource_dir)

    mapping = {}
    for key in manager.list():
        attr_name = sanitize_key_to_attr(key)
        mapping[attr_name] = key

    # Build @property methods for each asset
    properties = ""
    for attr, key in sorted(mapping.items()):
        properties += f"    @property\n"
        properties += f"    def {attr}(self):\n"
        properties += f"        \"\"\"Access asset: {key}\"\"\"\n"
        properties += f"        return self._manager[{repr(key)}]\n\n"

    # Build full source content
    content = (
        f"from pathlib import Path\n"
        f"from assetkit import AssetManager\n\n"
        f"_assets = AssetManager(package_root=Path(__file__).parent, resource_dir={repr(resource_dir)})\n\n"
        f"class AssetsProxy:\n"
        f"    def __init__(self, manager):\n"
        f"        self._manager = manager\n\n"
        f"{properties}"
        f"assets = AssetsProxy(_assets)\n"
    )

    # Write to package root
    output_path = package_path / output_filename
    output_path.write_text(content.strip() + "\n", encoding="utf-8")

    print(f"[AssetKit] [OK] Generated asset mapping file: {output_path}")

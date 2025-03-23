import os
from pathlib import Path

TEMPLATE = {
    "pyproject.toml": """[project]
name = "{name}"
version = "0.1.0"
description = "Generated asset package using AssetKit"
authors = [{{name = "Generated User", email = "user@example.com"}}]
readme = "README.md"
requires-python = ">=3.8"

[tool.setuptools.package-data]
{name} = ["resources/**/*"]

[project.entry-points."assetkit.assets"]
{name} = "{name}"
""",
    "__init__.py": "# {name} package",
    "README.md": "# {name}\n\nThis is an AssetKit-generated package containing structured assets.",
    "main.py": """from assetkit.asset_manager import AssetManager
from assetkit.discovery import discover_asset_managers

# Load assets directly from this package
assets = AssetManager(package_root=\"{name}\", resource_dir=\"resources\")

print(\"Welcome to your AssetKit asset package!\")

asset_list = assets.list()
if asset_list:
    print(\"Assets discovered in this package:\")
    for path in asset_list:
        print(f\" - {{path}}\")
else:
    print(\"No assets found yet. Add files to the 'resources/' directory inside your package.\")

# Discover assets from all installed packages
print(\"All discovered asset packages via AssetKit discovery:\")
try:
    discovered = discover_asset_managers()
    for pkg, mgr in discovered.items():
        print(f\"[{{pkg}}] -> {{mgr.list()}}\")
except Exception as e:
    print(f\"Discovery error: {{e}}\")
"""
}

def create_package(name: str, path="."):
    pkg_root = Path(path) / name
    pkg_dir = pkg_root / name
    resources = pkg_dir / "resources"

    pkg_root.mkdir(parents=True, exist_ok=True)
    pkg_dir.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)

    (pkg_root / "pyproject.toml").write_text(TEMPLATE["pyproject.toml"].format(name=name))
    (pkg_root / "README.md").write_text(TEMPLATE["README.md"].format(name=name))
    (pkg_dir / "__init__.py").write_text(TEMPLATE["__init__.py"].format(name=name))
    (pkg_root / "main.py").write_text(TEMPLATE["main.py"].format(name=name))

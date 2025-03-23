# 📦 AssetKit

> A Python toolkit for packaging, discovering, and loading structured runtime assets.

[![PyPI version](https://img.shields.io/pypi/v/assetkit)](https://pypi.org/project/assetkit/)
[![License](https://img.shields.io/pypi/l/assetkit)](https://github.com/docdann/assetkit/blob/main/LICENSE)
[![CI](https://github.com/docdann/assetkit/actions/workflows/ci.yml/badge.svg)](https://github.com/docdann/assetkit/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/docdann/assetkit/branch/main/graph/badge.svg)](https://codecov.io/gh/docdann/assetkit)

---

## 🚀 Features

- ✅ Structured asset packaging with a clean `resources/assets/` convention  
- ✅ `AssetManager`: Pythonic runtime asset access interface  
- ✅ CLI scaffolding for creating reusable asset packages and app templates  
- ✅ Optional asset injection at creation (`--add <files/dirs>`)  
- ✅ Optional install-after-generation (`--install`)  
- ✅ Auto-discovery of installed asset packages via `entry_points`  
- ✅ Fully pip-installable asset bundles — no runtime source directory needed  
- ✅ Works with plain files, binaries, or entire GitHub repositories

---

## 📦 Installation

```bash
pip install assetkit
```

During development:
```bash
pip install -e .
```

---

## 🛠 CLI Usage

### Create a new asset package:

```bash
assetkit new my_assets
```

With additional asset files or folders injected at creation time:

```bash
assetkit new my_assets --add /path/to/data.csv /path/to/config/
```

Auto-install the package after creation:

```bash
assetkit new my_assets --install
```

### Scaffold an AI/ML application project:

```bash
assetkit scaffold mlkit my_app_project
```

---

## 📂 Example Asset Package Structure

```
my_assets/
├── pyproject.toml
├── setup.cfg
├── MANIFEST.in
└── my_assets/
    ├── __init__.py
    └── resources/
        └── assets/
            ├── config/
            │   └── model.yaml
            ├── data/
            │   └── sample.csv
            └── github_repo/
                └── ...
```

---

## ⚡ Quick Python Usage Example

```python
from assetkit.asset_manager import AssetManager

assets = AssetManager(package_root="my_assets", resource_dir="resources/assets")
print(assets.list())  # List available assets
print(assets["config/model.yaml"].text())  # Read asset file
```

## 🔍 Discover All Installed Asset Packages

```python
from assetkit.discovery import discover_asset_managers

packages = discover_asset_managers()
for name, assets in packages.items():
    print(f"{name}: {assets.list()}")
```

---

## 🧪 Testing an Installed Asset Package

After creating and installing:

```bash
cd my_assets
pip install .
```

Then test in Python:

```python
from assetkit import AssetManager
assets = AssetManager(package_root="my_assets", resource_dir="resources/assets")
print(assets.list())
```

---

## 🐳 Dockerized Example (Optional)

You can build reproducible asset packages in Docker:

```dockerfile
FROM python:3.12-slim
RUN pip install assetkit
WORKDIR /app
RUN assetkit new my_assets
RUN mkdir -p /app/my_assets/my_assets/resources/assets && echo "Hello" > /app/my_assets/my_assets/resources/assets/hello.txt
WORKDIR /app/my_assets
RUN pip install .
CMD ["python", "-c", "from assetkit import AssetManager; assets = AssetManager(package_root='my_assets', resource_dir='resources/assets'); print(assets.list())"]
```

---

## 📄 License

MIT — See [LICENSE](LICENSE)

---

## 📬 More Info

- [GitHub Repository](https://github.com/docdann/assetkit)
- [PyPI Project Page](https://pypi.org/project/assetkit/)

---

## 🏁 Coming Soon (Roadmap)

- `assetkit bundle` and `assetkit extract` CLI tools  
- YAML and pandas extensions (`assetkit.ext.*`)  
- Language-agnostic manifest support via `assetkit.yaml`  
- Cross-platform asset publishing and usage

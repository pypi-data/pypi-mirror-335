from importlib.metadata import entry_points
from assetkit.asset_manager import AssetManager

def discover_asset_managers(group="assetkit.assets") -> dict:
    managers = {}
    eps = entry_points()
    selected = eps.select(group=group) if hasattr(eps, "select") else eps.get(group, [])

    for ep in selected:
        pkg_name = ep.name
        mod = ep.value
        try:
            managers[pkg_name] = AssetManager(package_root=mod, resource_dir="resources")
        except Exception as e:
            print(f"Failed to load assets for {pkg_name}: {e}")
    return managers

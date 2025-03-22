from assetkit import AssetManager
import pandas as pd

assets = AssetManager(package_root="mlkit_resources", resource_dir="resources/assets")

def load_dataset():
    csv_path = assets["data/sample.csv"].path()
    return pd.read_csv(csv_path)

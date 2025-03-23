import yaml
from assetkit import AssetManager
from sklearn.linear_model import LogisticRegression

assets = AssetManager(package_root="mlkit_resources", resource_dir="resources/assets")

def build_model():
    config_path = assets["config/model.yaml"].path()
    with open(config_path) as f:
        config = yaml.safe_load(f)

    model_params = config.get("model", {})
    if not isinstance(model_params, dict):
        model_params = {}

    return LogisticRegression(**model_params)

from .data_loader import load_dataset
from .model import build_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from assetkit import AssetManager
from pathlib import Path

assets = AssetManager(package_root="mlkit_resources", resource_dir="resources/assets")

def train():
    df = load_dataset()
    X = df.drop("target", axis=1)
    y = df["target"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = build_model()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    score = accuracy_score(y_test, y_pred)
    print(f"[{{PROJECT_NAME}}] Accuracy: {score:.4f}")
    model_path = Path(assets._base) / "models" / "pretrained.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"[{{PROJECT_NAME}}] Model saved to: {model_path}")

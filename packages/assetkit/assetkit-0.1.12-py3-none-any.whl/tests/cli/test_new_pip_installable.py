import subprocess
import tempfile
from pathlib import Path
import sys

def test_assetkit_new_project_is_pip_installable():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_name = "test_assets"
        subprocess.run(
            ["assetkit", "new", project_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        pkg_path = tmp_path / project_name
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "."],
            cwd=pkg_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"pip install failed: {result.stderr}"
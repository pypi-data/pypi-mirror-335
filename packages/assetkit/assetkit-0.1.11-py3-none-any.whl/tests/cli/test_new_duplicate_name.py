import subprocess
import tempfile
from pathlib import Path

def test_assetkit_new_project_duplicate_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_name = "test_assets"
        (tmp_path / project_name).mkdir()

        result = subprocess.run(
            ["assetkit", "new", project_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "already exists" in result.stdout
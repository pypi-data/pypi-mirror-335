import subprocess
import tempfile
from pathlib import Path

def test_assetkit_new_project_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_name = "test_assets"
        result = subprocess.run(
            ["assetkit", "new", project_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        target_path = tmp_path / project_name
        assert target_path.exists()
        assert (target_path / "setup.cfg").exists()
        assert (target_path / "pyproject.toml").exists()
        assert (target_path / "MANIFEST.in").exists()

        # Confirm placeholder was replaced
        content = (target_path / "setup.cfg").read_text()
        assert f"name = {project_name}" in content
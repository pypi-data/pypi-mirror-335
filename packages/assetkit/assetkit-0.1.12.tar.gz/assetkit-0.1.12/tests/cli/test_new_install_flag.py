import subprocess
import tempfile
from pathlib import Path

def test_assetkit_new_project_with_install():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_name = "test_assets"

        result = subprocess.run(
            ["assetkit", "new", project_name, "--install"],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        # CLI should succeed
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Check that expected files exist
        target_path = tmp_path / project_name
        assert target_path.exists()
        assert (target_path / "setup.cfg").exists()
        assert (target_path / "pyproject.toml").exists()
        assert (target_path / "MANIFEST.in").exists()

        # Check that installation was attempted
        assert "[AssetKit DEBUG] Installing package using 'pip install .'" in result.stdout

import subprocess
import tempfile
from pathlib import Path

def test_assetkit_new_project_with_invalid_asset():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_name = "test_assets"

        # Path that doesn't exist
        fake_asset = tmp_path / "nonexistent.txt"

        result = subprocess.run(
            ["assetkit", "new", project_name, "--add", str(fake_asset)],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0  # Still succeeds
        assert "WARNING" in result.stdout.upper() or result.stderr.upper()

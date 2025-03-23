import subprocess
import tempfile
from pathlib import Path

def test_assetkit_new_project_add_assets():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        project_name = "test_assets"
        asset_dir = tmp_path / "extra_assets"
        asset_dir.mkdir()
        sample_file = asset_dir / "hello.txt"
        sample_file.write_text("Hello from test asset")

        result = subprocess.run(
            ["assetkit", "new", project_name, "--add", str(sample_file)],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        asset_copied = tmp_path / project_name / project_name / "resources" / "assets" / "hello.txt"
        assert asset_copied.exists(), "Asset file was not copied correctly"
        assert "Hello from test asset" in asset_copied.read_text()

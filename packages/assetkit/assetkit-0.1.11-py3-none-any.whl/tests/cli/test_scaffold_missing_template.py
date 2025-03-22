import subprocess
import tempfile
from pathlib import Path

def test_assetkit_scaffold_missing_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        app_type = "nonexistent"
        project_name = "bad_project"

        result = subprocess.run(
            ["assetkit", "scaffold", app_type, project_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Template not found" in result.stdout
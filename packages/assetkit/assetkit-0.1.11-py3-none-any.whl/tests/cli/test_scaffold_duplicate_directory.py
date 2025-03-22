import subprocess
import tempfile
from pathlib import Path

def test_assetkit_scaffold_duplicate_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        app_type = "mlkit"
        project_name = "duplicate_project"

        # Prepare dummy directory
        (tmp_path / project_name).mkdir(parents=True)

        result = subprocess.run(
            ["assetkit", "scaffold", app_type, project_name],
            cwd=tmp_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "already exists" in result.stdout
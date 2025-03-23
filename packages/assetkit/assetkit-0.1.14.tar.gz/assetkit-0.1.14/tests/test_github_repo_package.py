import subprocess
import pytest

# Test Dockerfile build
def test_dockerfile_build_github_repo_package():
    result = subprocess.run(['docker', 'build', '-t', 'assetkit-test', './examples/github_repo_package/'], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"

# Test AssetKit installation
def test_assetkit_installed_github_repo_package():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'assetkit', '--help'], capture_output=True, text=True)
    assert result.returncode == 0, f"AssetKit installation failed: {result.stderr}"
    assert "new" in result.stdout, f"Expected 'new' in AssetKit help output: {result.stdout}"
    assert "scaffold" in result.stdout, f"Expected 'scaffold' in AssetKit help output: {result.stdout}"

# Test GitHub repository cloning
def test_github_repo_cloned():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'ls', '/app/my_assets/my_assets/resources/assets/github_repo'], capture_output=True, text=True)
    assert result.returncode == 0, f"GitHub repository clone failed: {result.stderr}"
    assert "README" in result.stdout, f"Expected 'README' in cloned repository: {result.stdout}"

# Test asset package installation
def test_asset_package_installed():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'pip', 'show', 'my-assets'], capture_output=True, text=True)
    assert result.returncode == 0, f"Asset package installation failed: {result.stderr}"
    assert "Version" in result.stdout, f"Package version not found in output: {result.stdout}"

# Test runtime asset list
def test_assetkit_runtime_assets():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'python', '-c', 'from assetkit import AssetManager; assets = AssetManager(package_root="my_assets", resource_dir="resources/assets"); print("Assets at runtime:", assets.list())'], capture_output=True, text=True)
    assert result.returncode == 0, f"Runtime test failed: {result.stderr}"
    assert "Assets at runtime:" in result.stdout, f"Unexpected output: {result.stdout}"

import subprocess
import pytest

def test_dockerfile_build():
    result = subprocess.run(['docker', 'build', '-t', 'assetkit-test', './examples/github_binary_install/'], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"

def test_assetkit_installed():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'assetkit', '--help'], capture_output=True, text=True)
    assert result.returncode == 0, f"AssetKit installation failed: {result.stderr}"
    # Check if 'new' and 'scaffold' commands are in the help output
    assert "new" in result.stdout, f"Expected 'new' in AssetKit help output: {result.stdout}"
    assert "scaffold" in result.stdout, f"Expected 'scaffold' in AssetKit help output: {result.stdout}"

def test_github_binary_installed():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'gh', '--version'], capture_output=True, text=True)
    assert result.returncode == 0, f"GitHub CLI installation failed: {result.stderr}"
    assert "gh" in result.stdout, f"GitHub CLI version output is incorrect: {result.stdout}"

def test_assetkit_functionality():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'assetkit', 'new', '--help'], capture_output=True, text=True)
    assert result.returncode == 0, f"AssetKit 'new' command failed: {result.stderr}"
    # Check if the output contains the name argument description
    assert "Name of the new asset package project" in result.stdout, f"Unexpected output: {result.stdout}"

def test_container_runtime():
    result = subprocess.run(['docker', 'run', '--rm', 'assetkit-test', 'bash', '-c', 'echo "Container is running!"'], capture_output=True, text=True)
    assert result.returncode == 0, f"Container runtime failed: {result.stderr}"
    assert "Container is running!" in result.stdout, f"Unexpected output: {result.stdout}"

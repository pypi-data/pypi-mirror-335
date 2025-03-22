
import shutil
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "asset_package"

def register_new_command(subparsers):
    parser = subparsers.add_parser("new", help="Create a new AssetKit asset package project")
    parser.add_argument("name", type=str, help="Name of the new asset package project")
    parser.set_defaults(func=create_new_project)

def create_new_project(args):
    project_name = args.name
    target_path = Path.cwd() / project_name

    if target_path.exists():
        print(f"[AssetKit] Directory '{project_name}' already exists.")
        return

    print(f"[AssetKit DEBUG] Copying from template: {TEMPLATE_DIR}")
    print(f"[AssetKit DEBUG] Target path: {target_path}")

    # Copy full template to target directory
    shutil.copytree(TEMPLATE_DIR, target_path)

    # Show copied structure
    print("[AssetKit DEBUG] Files copied to target path:")
    for path in target_path.rglob("*"):
        print("  -", path.relative_to(target_path))

    # Rename 'your_package_name' dir inside new project if it exists
    old_package_dir = target_path / "your_package_name"
    new_package_dir = target_path / project_name
    if old_package_dir.exists():
        print(f"[AssetKit DEBUG] Renaming {old_package_dir} -> {new_package_dir}")
        old_package_dir.rename(new_package_dir)

    # Replace placeholders like {{PROJECT_NAME}} in all files
    print("[AssetKit DEBUG] Replacing {{PROJECT_NAME}} placeholders...")
    for path in target_path.rglob("*"):
        if path.is_file():
            try:
                content = path.read_text()
                content = content.replace("{{PROJECT_NAME}}", project_name)
                path.write_text(content)
            except UnicodeDecodeError:
                # Skip non-text files
                print(f"[AssetKit DEBUG] Skipped binary file: {path}")
                continue

    print(f"[AssetKit] Asset package project '{project_name}' created successfully at ./{project_name}/")

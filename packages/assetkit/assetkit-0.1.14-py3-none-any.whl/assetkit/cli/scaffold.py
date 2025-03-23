
import shutil
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).parent.parent / "templates" / "scaffolds"

def register_scaffold_command(subparsers):
    parser = subparsers.add_parser("scaffold", help="Scaffold a new consumer application project")
    parser.add_argument("app_type", type=str, help="Application type (e.g., 'mlkit')")
    parser.add_argument("name", type=str, help="Name of the new application project")
    parser.set_defaults(func=lambda args: scaffold_project(args.app_type, args.name))

def scaffold_project(app_type, name):
    template_dir = TEMPLATE_ROOT / app_type
    if not template_dir.exists():
        print(f"[AssetKit Scaffold] Template not found: {template_dir}")
        return

    target_path = Path.cwd() / name
    if target_path.exists():
        print(f"[AssetKit Scaffold] Directory '{name}' already exists.")
        return

    shutil.copytree(template_dir, target_path)

    # Rename directory if needed (optional)
    print(f"[AssetKit Scaffold] Project scaffolded at ./{name}/")
    print("[AssetKit Scaffold] Replacing placeholders...")

    for path in target_path.rglob("*"):
        if path.is_file():
            try:
                content = path.read_text(encoding="utf-8")
                content = content.replace("{{PROJECT_NAME}}", name)
                path.write_text(content, encoding="utf-8")
            except (UnicodeDecodeError, ValueError):
                print(f"[AssetKit Scaffold] Skipped binary or unreadable file: {path}")
                continue

import argparse

def main():
    from . import new
    from . import scaffold

    parser = argparse.ArgumentParser(prog="assetkit", description="AssetKit CLI")
    subparsers = parser.add_subparsers(dest="command")

    new.register_new_command(subparsers)
    scaffold.register_scaffold_command(subparsers)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

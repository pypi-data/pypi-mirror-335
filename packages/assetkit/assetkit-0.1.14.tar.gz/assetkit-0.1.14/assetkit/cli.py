import sys
from assetkit.scaffold import create_package

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "new":
        print("Usage: assetkit new <package_name>")
        return
    name = sys.argv[2]
    create_package(name)
    print(f"Created new asset package: {name}")

import argparse
import sys
from core import trainer

print("[DEBUG] cli.py is running")

def main():
    print("[DEBUG] Inside main()")
    parser = argparse.ArgumentParser(description="my_app_project CLI")
    parser.add_argument("command", choices=["train", "evaluate", "shell"], help="Command to run")
    args = parser.parse_args()
    print(f"[DEBUG] Parsed command: {args.command}")

    if args.command == "train":
        print("[DEBUG] Calling trainer.train()...")
        try:
            trainer.train()
        except Exception as e:
            print("[ERROR] Exception in trainer.train():", e, file=sys.stderr)
    elif args.command == "evaluate":
        print("[DEBUG] Evaluation not implemented yet.")
    elif args.command == "shell":
        print("[DEBUG] Entering shell...")
        import code
        code.interact(local=globals())

if __name__ == "__main__":
    print("[DEBUG] __main__ block hit")
    main()

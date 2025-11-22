#!/usr/bin/env python3
import sys
import subprocess


def run_lint():
    black_result = subprocess.run(["poetry", "run", "black", "."])
    flake8_result = subprocess.run(["poetry", "run", "flake8", "."])
    # Check if either failed
    if black_result.returncode != 0 or flake8_result.returncode != 0:
        print("\n💥 Linting failed! See detailed errors above.")
        sys.exit(1)
    else:
        print("\n✅ All linting checks passed!")


def main():
    if len(sys.argv) != 2 or sys.argv[1] != "lint":
        print("Usage: ./notes-cli.py lint")
        sys.exit(1)
    run_lint()


if __name__ == "__main__":
    main()

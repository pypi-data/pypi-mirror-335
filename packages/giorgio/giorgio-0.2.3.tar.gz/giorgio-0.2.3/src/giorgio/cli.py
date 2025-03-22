#!/usr/bin/env python3
"""
Command Line Interface for Giorgio.

Available commands:
  - init       : Initialize a new Giorgio project.
  - new-script : Generate a new blank script.
  - start      : Launch the Giorgio GUI.
  - build      : Build an installable project package.
"""

import argparse
import os
import shutil
from giorgio.giorgio import main as start_gui  # type: ignore


def init_project() -> None:
    """
    Initialize a new Giorgio project by creating required directories and files.
    
    Creates 'scripts' directory, and configuration files 'config.json' and 'README.md'
    if they do not already exist.
    """
    if not os.path.exists("scripts"):
        os.makedirs("scripts")
        print("Created scripts directory.")
    else:
        print("scripts directory already exists.")

    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            f.write("{}")
        print("Created config.json.")
    else:
        print("config.json already exists.")

    if not os.path.exists("README.md"):
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# New Giorgio Project\n\nDocumentation for your project.")
        print("Created README.md.")
    else:
        print("README.md already exists.")

    print("Project initialization complete.")


def new_script(script_name: str) -> None:
    """
    Generate a new blank script using the internal template.

    The new script is created in the 'scripts' folder with the provided name.
    
    :param script_name: Name for the new script (without extension).
    """
    target_path = os.path.join("scripts", f"{script_name}.py")
    package_dir = os.path.dirname(__file__)
    source_template = os.path.join(package_dir, "internal_scripts", "blank_script.py")

    if not os.path.exists(source_template):
        print("Template script not found.")
        return
    if os.path.exists(target_path):
        print(f"Script '{target_path}' already exists.")
        return

    shutil.copy(source_template, target_path)
    print(f"New script created at '{target_path}'.")


def start_project() -> None:
    """
    Launch the Giorgio GUI.
    """
    print("Starting the Giorgio GUI...")
    start_gui()


def build_project() -> None:
    """
    Build an installable package of the project.

    This function is a placeholder; in a real scenario, it may invoke packaging tools.
    """
    print("Building project... (not yet implemented)")
    # Potentially call packaging tools like PyInstaller here.


def main() -> None:
    """
    Parse CLI arguments and execute the corresponding command.
    """
    parser = argparse.ArgumentParser(
        description="Giorgio CLI - Manage your automation project."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialize a new Giorgio project")

    parser_new = subparsers.add_parser("new-script", help="Generate a new script")
    parser_new.add_argument("script_name", type=str, help="Name of the new script")

    subparsers.add_parser("start", help="Launch the Giorgio GUI")
    subparsers.add_parser("build", help="Build an installable package of your project")

    args = parser.parse_args()

    if args.command == "init":
        init_project()
    elif args.command == "new-script":
        new_script(args.script_name)
    elif args.command == "start":
        start_project()
    elif args.command == "build":
        build_project()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

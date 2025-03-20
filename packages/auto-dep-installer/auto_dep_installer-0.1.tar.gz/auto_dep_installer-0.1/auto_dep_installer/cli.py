# auto_dep_installer/auto_dep_installer/cli.py

import argparse
import os
import sys
import venv
from pathlib import Path

from .installer import install_missing_packages
from .scanner import scan_directory_for_imports

def create_venv(venv_path):
    """Create a virtual environment at the specified path."""
    print(f"Creating virtual environment at {venv_path}...")
    venv.create(venv_path, with_pip=True)
    print(f"Virtual environment created successfully.")

def get_venv_activate_script(venv_path):
    """Get the path to the activation script based on the platform."""
    if sys.platform == "win32":
        return os.path.join(venv_path, "Scripts", "activate.bat")
    else:
        return os.path.join(venv_path, "bin", "activate")

def activate_venv(venv_path):
    """Modify environment to use the virtual environment."""
    activate_script = get_venv_activate_script(venv_path)
    
    if sys.platform == "win32":
        # On Windows, modify PATH to include the venv's Scripts directory
        scripts_dir = os.path.join(venv_path, "Scripts")
        os.environ["PATH"] = f"{scripts_dir};{os.environ['PATH']}"
    else:
        # On Unix, modify PATH to include the venv's bin directory
        bin_dir = os.path.join(venv_path, "bin")
        os.environ["PATH"] = f"{bin_dir}:{os.environ['PATH']}"
    
    # Set VIRTUAL_ENV environment variable
    os.environ["VIRTUAL_ENV"] = str(venv_path)
    
    # Update sys.prefix and sys.exec_prefix
    sys.prefix = str(venv_path)
    sys.exec_prefix = str(venv_path)
    
    # Remove PYTHONHOME if set
    if "PYTHONHOME" in os.environ:
        del os.environ["PYTHONHOME"]
    
    print(f"Virtual environment activated: {venv_path}")

def main():
    parser = argparse.ArgumentParser(description="Auto Dependency Installer")
    parser.add_argument(
        "--directory", "-d", 
        default=".", 
        help="Directory to scan for Python files (default: current directory)"
    )
    parser.add_argument(
        "--venv", "-v", 
        default=".venv", 
        help="Virtual environment name/path (default: .venv)"
    )
    parser.add_argument(
        "--no-venv", 
        action="store_true", 
        help="Skip virtual environment creation/activation"
    )
    parser.add_argument(
        "--custom-mappings", "-m",
        help="Path to JSON file with custom module-to-package mappings"
    )
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute
    project_dir = os.path.abspath(args.directory)
    venv_path = os.path.abspath(args.venv)
    
    # Create and activate virtual environment if requested
    if not args.no_venv:
        if not os.path.exists(venv_path):
            create_venv(venv_path)
        activate_venv(venv_path)
    
    print(f"Scanning directory: {project_dir}")
    imported_modules = scan_directory_for_imports(project_dir)
    
    # Load custom mappings if provided
    custom_mappings = {}
    if args.custom_mappings and os.path.exists(args.custom_mappings):
        import json
        with open(args.custom_mappings, 'r') as f:
            custom_mappings = json.load(f)
    
    # Install missing packages
    install_missing_packages(imported_modules, custom_mappings)
    
    print("Auto Dependency Installer completed successfully.")

if __name__ == "__main__":
    main()
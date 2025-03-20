#!/usr/bin/env python3
"""
Juno Package Manager

This tool manages Juno packages and dependencies.
"""

import argparse
import os
import sys
import json
import shutil
import zipfile
import tempfile
import urllib.request
from pathlib import Path

# Default package repository URL
DEFAULT_REPO = "https://packages.junolang.org"

class JunoPackageManager:
    """Juno package manager."""
    
    def __init__(self, repo_url=DEFAULT_REPO):
        """
        Initialize the package manager.
        
        Args:
            repo_url (str): URL of the package repository
        """
        self.repo_url = repo_url
        
        # Get the Juno home directory
        self.juno_home = os.environ.get("JUNO_HOME")
        if not self.juno_home:
            # Default to ~/.juno
            self.juno_home = os.path.expanduser("~/.juno")
        
        # Create the packages directory if it doesn't exist
        self.packages_dir = os.path.join(self.juno_home, "packages")
        os.makedirs(self.packages_dir, exist_ok=True)
        
        # Load the package index
        self.index_file = os.path.join(self.juno_home, "package_index.json")
        self.index = self._load_index()
    
    def _load_index(self):
        """
        Load the package index.
        
        Returns:
            dict: The package index
        """
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading package index: {e}", file=sys.stderr)
        
        # Return an empty index if the file doesn't exist or couldn't be loaded
        return {"packages": {}}
    
    def _save_index(self):
        """Save the package index."""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving package index: {e}", file=sys.stderr)
    
    def install(self, package_name, version=None):
        """
        Install a package.
        
        Args:
            package_name (str): Name of the package to install
            version (str): Version of the package to install, or None for latest
            
        Returns:
            bool: True if the package was installed, False otherwise
        """
        print(f"Installing package: {package_name}" + (f" (version {version})" if version else ""))
        
        # For now, we'll simulate package installation
        # In a real implementation, this would download and install the package
        
        # Check if the package is already installed
        if package_name in self.index["packages"]:
            installed_version = self.index["packages"][package_name]["version"]
            if version and version == installed_version:
                print(f"Package {package_name} version {version} is already installed")
                return True
            elif not version:
                print(f"Package {package_name} version {installed_version} is already installed")
                return True
        
        # Simulate downloading and installing the package
        print(f"Downloading package {package_name}...")
        
        # Create a dummy package directory
        package_dir = os.path.join(self.packages_dir, package_name)
        os.makedirs(package_dir, exist_ok=True)
        
        # Create a dummy package.json file
        package_json = {
            "name": package_name,
            "version": version or "1.0.0",
            "description": f"Dummy package for {package_name}",
            "dependencies": {}
        }
        
        with open(os.path.join(package_dir, "package.json"), 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        
        # Create a dummy source file
        with open(os.path.join(package_dir, f"{package_name}.juno"), 'w', encoding='utf-8') as f:
            f.write(f"// {package_name} package\n")
            f.write(f"func {package_name}_version() {{\n")
            f.write(f'    return "{version or "1.0.0"}";\n')
            f.write("}\n")
        
        # Update the package index
        self.index["packages"][package_name] = {
            "version": version or "1.0.0",
            "path": package_dir
        }
        
        self._save_index()
        
        print(f"Package {package_name} installed successfully")
        return True
    
    def uninstall(self, package_name):
        """
        Uninstall a package.
        
        Args:
            package_name (str): Name of the package to uninstall
            
        Returns:
            bool: True if the package was uninstalled, False otherwise
        """
        print(f"Uninstalling package: {package_name}")
        
        # Check if the package is installed
        if package_name not in self.index["packages"]:
            print(f"Package {package_name} is not installed")
            return False
        
        # Get the package directory
        package_dir = self.index["packages"][package_name]["path"]
        
        # Remove the package directory
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        
        # Remove the package from the index
        del self.index["packages"][package_name]
        
        self._save_index()
        
        print(f"Package {package_name} uninstalled successfully")
        return True
    
    def list_packages(self):
        """
        List installed packages.
        
        Returns:
            list: List of installed packages
        """
        if not self.index["packages"]:
            print("No packages installed")
            return []
        
        print("Installed packages:")
        packages = []
        for name, info in self.index["packages"].items():
            version = info["version"]
            print(f"  {name} ({version})")
            packages.append({"name": name, "version": version})
        
        return packages
    
    def search(self, query):
        """
        Search for packages.
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of matching packages
        """
        print(f"Searching for packages matching '{query}'...")
        
        # In a real implementation, this would search the package repository
        # For now, we'll return some dummy results
        
        results = []
        if "juno" in query.lower():
            results.append({
                "name": "juno-core",
                "version": "1.0.0",
                "description": "Core Juno libraries"
            })
            results.append({
                "name": "juno-extras",
                "version": "0.5.0",
                "description": "Extra utilities for Juno"
            })
        
        if "math" in query.lower():
            results.append({
                "name": "juno-math",
                "version": "1.2.0",
                "description": "Mathematical functions for Juno"
            })
        
        if "web" in query.lower():
            results.append({
                "name": "juno-web",
                "version": "0.9.0",
                "description": "Web utilities for Juno"
            })
        
        if results:
            print(f"Found {len(results)} package(s):")
            for pkg in results:
                print(f"  {pkg['name']} ({pkg['version']}): {pkg['description']}")
        else:
            print(f"No packages found matching '{query}'")
        
        return results
    
    def create_package(self, name, version="0.1.0", description=""):
        """
        Create a new package.
        
        Args:
            name (str): Name of the package
            version (str): Version of the package
            description (str): Description of the package
            
        Returns:
            bool: True if the package was created, False otherwise
        """
        print(f"Creating package: {name} (version {version})")
        
        # Create the package directory
        package_dir = os.path.join(os.getcwd(), name)
        if os.path.exists(package_dir):
            print(f"Error: Directory already exists: {package_dir}", file=sys.stderr)
            return False
        
        os.makedirs(package_dir)
        
        # Create the package.json file
        package_json = {
            "name": name,
            "version": version,
            "description": description,
            "dependencies": {}
        }
        
        with open(os.path.join(package_dir, "package.json"), 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
        
        # Create the source directory
        src_dir = os.path.join(package_dir, "src")
        os.makedirs(src_dir)
        
        # Create a sample source file
        with open(os.path.join(src_dir, f"{name}.juno"), 'w', encoding='utf-8') as f:
            f.write(f"// {name} package\n")
            f.write(f"func {name}_version() {{\n")
            f.write(f'    return "{version}";\n')
            f.write("}\n")
        
        # Create a README file
        with open(os.path.join(package_dir, "README.md"), 'w', encoding='utf-8') as f:
            f.write(f"# {name}\n\n")
            f.write(f"{description}\n\n")
            f.write("## Installation\n\n")
            f.write(f"```bash\n")
            f.write(f"juno-package install {name}\n")
            f.write(f"```\n\n")
            f.write("## Usage\n\n")
            f.write(f"```juno\n")
            f.write(f"// Import the package\n")
            f.write(f"import {name};\n\n")
            f.write(f"// Use the package\n")
            f.write(f"Show({name}_version());\n")
            f.write(f"```\n")
        
        print(f"Package {name} created successfully in {package_dir}")
        return True

def main():
    """Main entry point for the package manager."""
    parser = argparse.ArgumentParser(description="Juno Package Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Package to install")
    install_parser.add_argument("--version", help="Version to install")
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("package", help="Package to uninstall")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed packages")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for packages")
    search_parser.add_argument("query", help="Search query")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new package")
    create_parser.add_argument("name", help="Package name")
    create_parser.add_argument("--version", default="0.1.0", help="Package version")
    create_parser.add_argument("--description", default="", help="Package description")
    
    args = parser.parse_args()
    
    # Create the package manager
    pm = JunoPackageManager()
    
    # Run the appropriate command
    if args.command == "install":
        pm.install(args.package, args.version)
    elif args.command == "uninstall":
        pm.uninstall(args.package)
    elif args.command == "list":
        pm.list_packages()
    elif args.command == "search":
        pm.search(args.query)
    elif args.command == "create":
        pm.create_package(args.name, args.version, args.description)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
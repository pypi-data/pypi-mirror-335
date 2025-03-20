# auto_dep_installer/auto_dep_installer/installer.py

import importlib
import subprocess
import sys
import pkg_resources

def is_module_installed(module_name):
    """Check if a module is installed and importable."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def get_installed_packages():
    """Get a dictionary of installed packages."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def install_package(package_name):
    """Install a package using pip."""
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package_name}: {e}")
        return False

def install_missing_packages(imported_modules, custom_mappings=None):
    """Install missing packages based on imported modules."""
    if custom_mappings is None:
        custom_mappings = {}
    
    # Common module-to-package mappings
    default_mappings = {
        "bs4": "beautifulsoup4",
        "PIL": "pillow",
        "cv2": "opencv-python",
        "sklearn": "scikit-learn",
        "yaml": "pyyaml",
        "wx": "wxpython",
        "matplotlib.pyplot": "matplotlib",
        "tensorflow.keras": "tensorflow",
    }
    
    # Combine default and custom mappings
    mappings = {**default_mappings, **custom_mappings}
    
    # Filter out standard library modules
    stdlib_modules = set(sys.modules.keys())
    
    installed_packages = get_installed_packages()
    to_install = []
    
    for module_name in imported_modules:
        # Skip standard library modules
        if module_name in stdlib_modules:
            continue
        
        # Get root module name (e.g., 'numpy' from 'numpy.array')
        root_module = module_name.split('.')[0]
        
        # Check if the module is already installed
        if is_module_installed(root_module):
            continue
        
        # Use mapping if available
        package_name = mappings.get(root_module, root_module)
        
        # Also check if the package is already installed under a different name
        if package_name.lower() in installed_packages:
            continue
            
        to_install.append(package_name)
    
    # Remove duplicates while preserving order
    to_install = list(dict.fromkeys(to_install))
    
    if not to_install:
        print("All dependencies are already installed.")
        return
    
    print(f"Found {len(to_install)} missing packages to install:")
    for package in to_install:
        print(f"  - {package}")
    
    # Install each package
    for package in to_install:
        install_package(package)
import subprocess
import sys
import importlib.util


def is_package_installed(package_name):
    return importlib.util.find_spec(package_name) is not None


REAL_PACKAGE = "fqtest"


GIT_URL = "git+https://github.com/NgocAnLam/fqtest.git@0.11.18"


if not is_package_installed(REAL_PACKAGE):
    try:
        print(f"Installing {REAL_PACKAGE} from GitHub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", GIT_URL])
        print(f"{REAL_PACKAGE} installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {REAL_PACKAGE}: {e}")
        sys.exit(1)


from fqtest import *  
import glob
import os

# Collect all modules dynamically
def __list_all_modules():
    modules = []
    files = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
    for f in files:
        name = os.path.basename(f)[:-3]
        if name == "__init__" or name.startswith("_"):
            continue
        modules.append(name)
    return modules

ALL_MODULES = __list_all_modules()

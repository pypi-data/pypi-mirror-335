import os, sys


def is_executable(path):
    """Check file is executable"""
    if sys.platform == 'win32':
        executable = os.access(path, os.X_OK) or path.lower().endswith(".cmd")
        return os.path.isfile(path) and executable
    return os.path.isfile(path) and os.access(path, os.X_OK)

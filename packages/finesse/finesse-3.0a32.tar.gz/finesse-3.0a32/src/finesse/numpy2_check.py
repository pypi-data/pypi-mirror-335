from packaging.version import parse
import warnings
import importlib


def check_numpy2_compatibility():
    """If NumPy 2 is installed, checks if finesse dependencies have the minimal version
    that supports NumPy 2."""

    import numpy

    if parse(numpy.__version__).major < 2:
        return

    # see https://github.com/numpy/numpy/issues/26191
    numpy2_versions = {
        "h5py": "3.11.0",
        "matplotlib": "3.8.4",
        "networkx": "3.3",
        "scipy": "1.13.0",
        "sympy": "1.12.1",
    }
    incompatible = {}

    for pkg, min_version in numpy2_versions.items():
        try:
            mod = importlib.import_module(pkg)
        except Exception as e:
            if "numpy" in e.args[0]:
                raise ImportError(
                    f"Numpy 2 incompatibility, please update '{pkg}' to {min_version} or higher"
                ) from e
            else:
                raise

        if parse(mod.__version__) < parse(min_version):
            incompatible[pkg] = mod.__version__

    if not incompatible:
        return

    msg = "NumPy 2 incompatible package versions discovered! Please update:\n"
    for pkg, version in incompatible.items():
        msg += f"{pkg}: {version} -> " f"{pkg}>={numpy2_versions[pkg]}\n"
    msg += "See https://github.com/numpy/numpy/issues/26191"
    warnings.warn(UserWarning(msg), stacklevel=1)

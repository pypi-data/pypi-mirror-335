"""Configuration module of slk."""

from __future__ import annotations

import os
import re
import shutil
import warnings
from pathlib import Path
from subprocess import PIPE, CalledProcessError, run
from typing import Any, Literal, Optional

from .constants import PYSLK_LOGGER, SLK, SLK_HELPERS

__all__ = ["get", "set", "module_load"]


class set:
    """Set pyslk configuration to intract with the slk backend.

    This class can be used to set specifics on the the backend version
    of slk, for example the path the th slk binary or the slk version.

    Parameters
    ----------
    **kwargs: str | Path
        key-value pairs of the config values to set.

    Examples
    --------
    Set the specific slk version that is loaded on startup:

    ::

        from pyslk import pyslk
        pyslk.config.set(slk_version="3.3.76")


    It would be also possible to set the path to the slk binary. By default
    the the set class checks the path to the binary of the slk command. To
    set a custom path you can use the ``slk`` key. This time we are using
    the context manager to temporarely override the default path.

    ::

        from pyslk import pyslk
        with pyslk.config.set(
            slk="/sw/spack-levante/slk-3.3.73-nl4md3/bin/slk",
            slk_helpers="/sw/spack-levante/slk-3.3.73-nl4md3/bin/slk_helpers"):
                print(pyslk.config.get("__slk_version__"))
                print(pyslk.config.get("__slk_helpers_version__"))
        print(pyslk.config.get("__slk_version__"))
        print(pyslk.config.get("__slk_helpers_version__"))

        #
        3.3.73
        1.5.7
        3.3.21
        1.2.4
    """

    config: dict[str, Optional[str]] = {
        SLK: SLK,
        SLK_HELPERS: SLK_HELPERS,
        "module": SLK,
        "module_helpers": SLK_HELPERS,
    }
    """Default slk/slk_helpers commands, stored in the config cache. These
    can either be commands (default) or abs paths to the binaries."""
    _record: list[tuple[Literal["insert", "replace"], str, Optional[str]]]

    def __init__(self, **kwargs: str | Path):
        self._record = []
        for key, value in kwargs.items():
            self._assign(key.lower(), str(value), self.config)

    def __enter__(self) -> set:
        return self

    def __exit__(self, *args: Any) -> None:
        for op, key, value in reversed(self._record):
            if op == "replace":
                self.config[key] = value
            else:  # insert
                self.config.pop(key, None)

    def _assign(
        self,
        key: str,
        value: str,
        cfg: dict[str, Optional[str]],
        record: bool = True,
    ):
        if record:
            if key in cfg:
                self._record.append(("replace", key, cfg[key]))
            else:
                self._record.append(("insert", key, None))
        cfg[key] = value

    def get_path(self, key: str) -> str | None:
        """Get the path to the binary of slk"""
        value = self.config.get(key, key)
        if value is None:
            return None
        if Path(value).expanduser().is_absolute():
            return str(Path(self.config[key]).expanduser())
        slk_path = shutil.which(value)
        if slk_path:
            return slk_path
        return None

    def get_version(self, command) -> str:
        """Get the version of a command"""
        slk_path = self.get_path(SLK)
        env = module_load()
        if slk_path:
            env["PATH"] = f"{Path(slk_path).parent}" + os.pathsep + env["PATH"]
        try:
            return re.search(
                r"\d+\.\d+\.\d+",
                (
                    run(
                        [command, "version"],
                        env=env,
                        stdout=PIPE,
                        stderr=PIPE,
                    ).stdout.decode("utf-8")
                ),
            ).group()
        except (CalledProcessError, FileNotFoundError, AttributeError):
            warnings.warn(f"failed to dertermine {command} version")
            return "0.0.0"


def module_load(
    module_path: str = "/usr/share/Modules/libexec/modulecmd.tcl",
    _env: dict[str, dict[str, str]] = {},
) -> dict[str, str]:
    """Use the module load command to activate the slk environment."""
    slk_version = get("slk_version", "")
    module_name = get("module", SLK)
    if slk_version:
        module_name = f"{module_name}/{slk_version}"
    # Check if slk is already present in the current path, of so
    # let's assume the user want's to use this version then
    if _config.get_path(SLK) is not None:
        PYSLK_LOGGER.debug("slk already in users path, skipping module load")
        return os.environ.copy()
    if _env.get(module_name) is None:
        PYSLK_LOGGER.debug("Loading slk module %s", module_name)
        _env[module_name] = {}
        try:
            res = (
                run(
                    [module_path, "python", "load", module_name],
                    check=True,
                    stdout=PIPE,
                    stderr=PIPE,
                )
                .stdout.decode()
                .split("\n")
            )
        except (FileNotFoundError, CalledProcessError) as error:
            warnings.warn(f"Could not load {module_name}: {error}")
            return {}
        for line in res:
            if "=" in line:
                key, _, value = line.partition("=")
                new_key = (re.findall(r"\['([^']*)", key.strip()) or [""])[0]
                if new_key.strip():
                    _env[module_name][new_key.strip()] = value.strip().replace("'", "")
    else:
        PYSLK_LOGGER.debug("module %s has already been loaded", module_name)
    return _env[module_name]


_config = set()


def get(key: str, default: Optional[str] = None) -> Optional[float]:
    """Get global slk config.

    Parameters
    ----------
    key: str
        config parameter to query
    default: str, default: None
        default return value
    """
    if key == "__slk_version__":
        return _config.get_version(SLK)
    if key == "__slk_helpers_version__":
        return _config.get_version(SLK_HELPERS)
    return _config.config.get(key.lower(), default)

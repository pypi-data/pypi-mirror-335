#!/usr/bin/env python

import inspect
import json
import shlex
import sys
from pathlib import Path
from typing import Any, Dict


def env_get(globals: Dict[str, Any]) -> Dict[str, str]:
    """Get environment variables from globals"""

    environments = {}
    for k, v in globals.items():
        if k.upper() == k:
            value = None
            if isinstance(v, str):
                value = v
            elif isinstance(v, Path):
                value = v.absolute().as_posix()
            elif isinstance(v, dict):
                value = json.dumps(v)
            else:
                value = str(v)
            environments[k] = value
    return environments


def env_export(env: Dict[str, str] = None):
    for k, v in env.items():
        print("export {}={}".format(k, shlex.quote(v)), file=sys.stdout)


def env_import(env: Dict[str, str]):
    import os

    for k, v in env.items():
        os.environ[k] = v


def env_auto():
    frame = inspect.stack()[1].frame
    globals = frame.f_locals
    env = env_get(globals)
    env_export(env)


if __name__ == "__main__":
    env_auto()

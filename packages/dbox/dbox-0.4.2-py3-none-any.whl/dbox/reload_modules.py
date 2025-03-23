import importlib
import logging
import sys
import types

log = logging.getLogger(__name__)


def reload_module_and_submodules(module):
    """
    Recursively reloads a module and all its submodules.

    :param module: The module to reload.
    """
    # Get the module name and its package name
    module_name = module.__name__
    package_name = module_name.split(".")[0]

    # Get all modules in the current package
    modules_to_reload = [module for name, module in sys.modules.items() if name.startswith(package_name + ".")]

    # Sort modules by their name length to ensure parent modules are reloaded first
    modules_to_reload.sort(key=lambda m: len(m.__name__))

    # Reload each module
    for mod in modules_to_reload:
        if isinstance(mod, types.ModuleType):
            log.info("Reloading module: %s", mod.__name__)
            importlib.reload(mod)

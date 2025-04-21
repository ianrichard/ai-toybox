import importlib
import pkgutil

for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name not in ("registry",):
        importlib.import_module(f"{__name__}.{module_name}")
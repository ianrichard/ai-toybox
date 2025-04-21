from typing import Callable, Dict, Any
from pydantic import create_model
import inspect

TOOL_FUNCS: Dict[str, Callable[..., Any]] = {}
TOOL_DESCRIPTIONS: Dict[str, str] = {}
TOOL_SCHEMAS: Dict[str, dict] = {}

def tool(func: Callable) -> Callable:
    sig = inspect.signature(func)
    fields = {}
    for name, param in sig.parameters.items():
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else (str if param.default == inspect.Parameter.empty else type(param.default))
        default = param.default if param.default != inspect.Parameter.empty else ...
        fields[name] = (annotation, default)
    InputModel = create_model(f"{func.__name__.title()}Input", **fields)
    TOOL_FUNCS[func.__name__] = func
    TOOL_DESCRIPTIONS[func.__name__] = func.__doc__ or ""
    TOOL_SCHEMAS[func.__name__] = InputModel.schema()
    return func
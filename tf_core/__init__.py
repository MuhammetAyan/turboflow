from abc import ABC, abstractmethod
from argparse import _SubParsersAction
import sys

class IApp(ABC):
    commands_map: dict
    
    @abstractmethod
    def add_parsers(parser: _SubParsersAction):
        pass

def tf_command(name:str):
    def decorator(func):
        module_str:str = func.__module__
        if module_str.endswith(".functions"):
            module_str = module_str[:-10]
        app = sys.modules[module_str]
        if not hasattr(app, "commands_map"):
            app.commands_map = {}
        app.commands_map.update({name: func})
        return func
    return decorator


from . import commands
from . import io
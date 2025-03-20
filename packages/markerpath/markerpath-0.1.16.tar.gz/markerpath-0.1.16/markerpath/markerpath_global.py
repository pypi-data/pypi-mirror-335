import os
import logging
from functools import wraps
from ggtoolset import ConfigReader
from ggtoolset.Utils import Logger
markerpath_global={}


def markerpath_global_initialize(args=None):
    """!
        This function will initialize the global context with the configuration, logger, device and the commandline arguments
        @param args: commandline arguments; exepcts to have the following attributes
            - config: path to the configuration file
            - log_level: log level for the logger
    """
    if 'config' not in markerpath_global:
        if args != None and hasattr(args,"config"):
            markerpath_global['config'] = _load_config(args.config)
        else:
            if os.path.isfile(os.path.join(os.environ['MARKERPATH'],"markerpath_config.xml")):
                markerpath_global['config'] = _load_config("markerpath_config.xml")
            elif os.path.isfile(os.path.join(os.environ['MARKERPATH'],"config/markerpath_config.xml")):
                markerpath_global['config'] = _load_config("config/markerpath_config.xml")
            else:
                markerpath_global['config'] = None
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR
    }
    level = log_levels.get(getattr(args, "log_level", "debug"), logging.DEBUG)   
    log_file=getattr(args, "log_file", None)
    if log_file is None:
        log_file="runtime.log"
    markerpath_global['logger'] = _setup_logger(level=level,log_file=log_file)   
    markerpath_global['args'] = args
    #markerpath_global['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
    return
def _load_config(config_path):
    """!
    Load the configuration file. Called by global_initialize
    """
    try:
        config = ConfigReader(os.path.join(os.environ['MARKERPATH'],config_path))()
    except Exception as e:
        print(f"Error loading config file {config_path} {str(e)}")
        raise 
    return config

def _setup_logger(level=logging.DEBUG,log_file:str=None)->logging.Logger:
    """!
    Setup the logger. Called by global_initialize
    """
    try:
        log_file=os.path.join(os.environ['MARKERPATH'],log_file)
        logger=Logger.get_logger(__name__, level=level, log_file=log_file)
    except Exception as e:
        print(f"Error setting up logger {str(e)}")
        raise 
    return logger

def change_logging_level(new_level):
    """!
    Change the logging level for the logger and all its handlers.
    """
    # Set the level on the logger itself (affects filtering at the logger level)
    markerpath_global['logger'].setLevel(new_level)
    # Update the level for each handler attached to this logger
    for handler in markerpath_global['logger'].handlers:
        handler.setLevel(new_level)
    return

def inject_logger_member(arg=None):
    """
    Decorator factory to inject a logger member into the class instance.
    
    Can be used as either:
      @inject_logger_member
      or
      @inject_logger_member("my_logger")
    """
    if callable(arg):
        # The decorator was applied without arguments.
        init = arg
        member_name = "logger"
        @wraps(init)
        def wrapped(self, *args, **kwargs):
            # Access the global markerpath_global dictionary.
            global markerpath_global
            if 'markerpath_global' not in globals() or not isinstance(markerpath_global, dict):
                raise Exception("from markerpath import markerpath_global, markerpath_global_initialize")
            if "logger" not in markerpath_global:
                markerpath_global_initialize()
            setattr(self, member_name, markerpath_global["logger"])
            result = init(self, *args, **kwargs)
            setattr(self, member_name, markerpath_global["logger"])            
            return result
        return wrapped
    else:
        # The decorator was applied with an argument.
        member_name = arg if arg is not None else "logger"
        def decorator(init):
            @wraps(init)
            def wrapped(self, *args, **kwargs):
                result = init(self, *args, **kwargs)
                global markerpath_global
                if 'markerpath_global' not in globals() or not isinstance(markerpath_global, dict):
                    raise Exception("from markerpath import markerpath_global, markerpath_global_initialize")
                if "logger" not in markerpath_global:
                    markerpath_global_initialize()
                setattr(self, member_name, markerpath_global["logger"])
                result = init(self, *args, **kwargs)
                setattr(self, member_name, markerpath_global["logger"])            
                return result
            return wrapped
        return decorator

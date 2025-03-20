import inspect
import importlib.util, importlib.metadata
import psutil
import platform
import os
import requests

import logging
logger = logging.getLogger(__name__)

class ColoredLoggimgFormatter(logging.Formatter):
    grey = "\033[30m"  # Standard grey/black color
    yellow = "\033[33m"  # Standard yellow
    red = "\033[31m"  # Standard red
    bold_red = "\033[1;31m"  # Bold red
    reset = "\033[0m"  # Reset to default
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def get_package_tree() -> list[str]:
  """
  Get the package tree of the caller
  """
  stack = inspect.stack()
  modules = [inspect.getmodule(f.frame) for f in stack if inspect.getmodule(f.frame)]
  packages = [module.__package__ for module in modules if module.__package__]
  return list(dict.fromkeys(packages)) # requires python >= 3.7

def get_caller_package_name() -> str | None:
  """
  Get the package name of the caller
  """
  packages = get_package_tree()
  
  # return the first package name after plausipy (this should always be [1])
  caller_package_name = packages[1] if len(packages) > 1 else None
  logger.info(f"Caller package {caller_package_name} from package tree: {packages}")
  
  return caller_package_name

def get_package_version(package_name: str | None) -> str | None:
  """ 
  Get the version of the package
  
  Args:
    package_name (str): The package name
  """
  if not package_name:
    return None
  version = importlib.metadata.version(package_name)
  return version

def get_usage_data():
    process = psutil.Process(os.getpid())
    return {
        "memory": process.memory_info().rss / (1024 ** 2), # in MB
        "cpu": process.cpu_percent()
    }

def get_system_data():
  return {
    "system": platform.system(),
    "release": platform.release(),
    #"version": platform.version(),
    "machine": platform.machine(),
    "processor": platform.processor(),
    "platform": platform.platform()
  }
  
def get_python_data():
  return {
    "version": platform.python_version(),
    "compiler": platform.python_compiler(),
    "implementation": platform.python_implementation(),
    # "build": platform.python_build(), # tuble..
    # "branch": platform.python_branch(),
    # "revision": platform.python_revision(),
  }
  
def get_localtion_data():
  response = requests.get('https://ipinfo.io/json')
  data = response.json()
  
  lat, lon = data["loc"].split(",")
  
  return {
    # "city": data["city"],
    "region": data["region"],
    "country": data["country"],
    # "loc": {
    #   "lat": lat,
    #   "lon": lon
    # },
    "timezone": data["timezone"],
  }

# test
if __name__ == "__main__":
  print(get_package_tree())
  print(get_caller_package_name())
  print(get_package_version("plausipy"))
  print(get_usage_data())
  print(get_system_data())
  print(get_python_data())
  print(get_localtion_data())
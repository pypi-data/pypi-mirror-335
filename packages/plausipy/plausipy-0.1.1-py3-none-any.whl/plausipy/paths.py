from pathlib import Path

BASE_DIR = Path.home() / ".plausipy"
# BASE_DIR = Path("/Users/lenny/Projects/plausipy-project/plausipy/no_access_dir") / ".plausipy"
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

CONFIG_FILE = CONFIG_DIR / "config.json"
IDS_FILE = CONFIG_DIR / "ids.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
from pathlib import Path
import os

import smartpark


PROJECT_ROOT_DIR = Path(smartpark.__file__).resolve().parent.parent
SMART_PARK_DIR = Path(smartpark.__file__).resolve().parent

DATA_DIR = PROJECT_ROOT_DIR / 'data'
CONFIG_DIR = PROJECT_ROOT_DIR / 'configurations'
LOG_DIR = PROJECT_ROOT_DIR / 'logs'

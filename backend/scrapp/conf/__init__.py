import importlib
import os

ENVIRONMENT_VARIABLE = "APP_SETTINGS_MODULE"
DEFAULT_SETTINGS_MODULE = "app.settings"

# Load the applications settings
APP_SETTINGS_MODULE = os.environ.get(ENVIRONMENT_VARIABLE, DEFAULT_SETTINGS_MODULE)
settings = importlib.import_module(APP_SETTINGS_MODULE)

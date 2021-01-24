import os

import yaml

from app.logger import get_logger, init_default_handler


# init variables
_global_config_rel_path = "../files/globals.cfg.yaml"
_global_config_abs_path = os.path.join(os.path.dirname(__file__), _global_config_rel_path)


# read configuration from global config file and flatten
with open(_global_config_abs_path) as in_stream:
    _global_config_data = yaml.safe_load(in_stream)


# flatten the config for the current environment
_base_config_data = _global_config_data.get("dev")
_base_config_data.update(_global_config_data.get(os.getenv("ENVIRONMENT", "dev")))


# create the global logger
log = get_logger(__name__, log_level=_base_config_data.get("log_level"))


# setup the default handler
init_default_handler(log, log_level=_base_config_data.get("log_level"))

import os
from app.utils.io_utils import get_abs_path, get_all_data_from_yaml
from app.logger import get_logger, init_default_handler


# init variables
_global_config_abs_path = get_abs_path(
    rel_path="../files/globals.cfg.yaml", caller_script_directory=__file__
)

# read configuration from global config file and flatten
_global_config_data = get_all_data_from_yaml(_global_config_abs_path)

# flatten the config for the current environment

base_config_data = _global_config_data.get("dev")
base_config_data.update(_global_config_data.get(os.getenv("ENVIRONMENT", "dev")))


# create the global logger
log = get_logger(__name__, log_level=base_config_data.get("log_level"))


# setup the default handler
init_default_handler(log, log_level=base_config_data.get("log_level"))

""" Contains utilities related to file io """
import os

import yaml


def get_all_data_from_yaml(yaml_file_path):
    with open(yaml_file_path) as in_stream:
        content = yaml.safe_load(in_stream)
        return content


def get_all_data_from_file(file_path):
    with open(file_path) as in_stream:
        return in_stream.read()


def get_abs_path(rel_path, caller_script_directory):
    return os.path.join(os.path.dirname(caller_script_directory), rel_path)

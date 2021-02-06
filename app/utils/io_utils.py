""" Contains utilities related to io """
import os
import getpass
import yaml


def get_all_data_from_yaml(yaml_file_path):
    with open(yaml_file_path) as in_stream:
        content = yaml.safe_load(in_stream) or {}
        return content


def get_all_data_from_file(file_path):
    with open(file_path) as in_stream:
        return in_stream.read()


def get_abs_path(rel_path, caller_script_directory):
    return os.path.join(os.path.dirname(caller_script_directory), rel_path)


def prompt(key, custom_sentence=None):
    if custom_sentence is None:
        custom_sentence = f"Enter your {key}: "
    if "pwd" in key or "password" in key:
        return getpass.getpass(custom_sentence)
    else:
        return input(custom_sentence)


def validate_keys(_dict, _list_keys, to_prompt=False):
    for key in _list_keys:
        if key not in _dict or _dict.get(key).strip() == "":
            if to_prompt:
                _dict[key] = prompt(key)
            else:
                return False
    return True

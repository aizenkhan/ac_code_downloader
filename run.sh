#!/bin/bash

curr_env="dev"
curr_dir=$(pwd)

set +a
export ENVIRONMENT=${curr_env}
export PYTHONPATH=${curr_dir}
set -a

python3 app/launcher.py

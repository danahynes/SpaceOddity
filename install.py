#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: install.py                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 08/31/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

import os
import shlex
import shutil
import subprocess

home_dir = os.path.expanduser('~')

# ------------------------------------------------------------------------------

# the program name
prog_name = 'spaceoddity'
app_dir = os.path.join(home_dir, f'.{prog_name}')

apt_reqs = [
    'python3-pip',
    'imagemagick'
]

pip_reqs = [
    'wand'
]

mk_dirs = [
    f'{app_dir}'
]

copy_files = {
    f'{prog_name}_main.py': f'{app_dir}'
}

run_path = os.path.join(app_dir, f'{prog_name}_main.py')

# ------------------------------------------------------------------------------

# get all requirements
print('Installing requirements...')

# get system requirements
for item in apt_reqs:
    print(f'Installing {item}...')
    cmd = f'sudo apt-get install {item}'
    cmd_array = shlex.split(cmd)
    try:
        subprocess.run(cmd_array)
    except subprocess.CalledProcessError as error:
        print(error.stderr.decode())

# get python requirements
for item in pip_reqs:
    print(f'Installing {item}...')
    cmd = f'pip install {item}'
    cmd_array = shlex.split(cmd)
    try:
        subprocess.run(cmd_array)
    except subprocess.CalledProcessError as error:
        print(error.stderr.decode())

# set up folders
print('Setting up folders...')

for item in mk_dirs:
    print(f'Making directory {item}...')
    os.makedirs(item, exist_ok=True)

# copy files
print('Copying files...')

# copy files
for key, value in copy_files.items():
    print(f'Copying {key} to {value}...')
    shutil.copy(key, value)

# run program now
print('Running program now...')
cmd_array = shlex.split(run_path)
try:
    subprocess.run(cmd_array)
except subprocess.CalledProcessError as error:
    print(error.stderr.decode())

# ------------------------------------------------------------------------------

# from crontab import CronTab

# -)

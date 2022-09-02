#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: install.py                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: make this a class with __init__, run, preflight, postflight

# TODO: learn more about setup.py and can we use it to install

# TODO: files and folders created during this session wil have owner/group set
# to root b/c script was called by sudo. NEED TO FIX THIS

'''
{
    user: {
        apt_reqs: {
            req1,
            req2
        }
        pip_reqs: {
            req1,
            req2
        }
        mkdirs: [
            dir1,
            dir2
        ],
        mkfiles: [
            file1,
            file2
        ]
        cp: {
            file1: dst1,
            file2: dst2,
        }
    },
    sudo: {
        apt_reqs: {
            req1,
            req2
        }
        pip_reqs: {
            req1,
            req2
        }
        requires: {
            cmd1,
            cmd2
        }
        mkdirs: [
            dir1,
            dir2
        ],
        mkfiles: [
            file1,
            file2
        ]
        cp: {
            file1: dst1,
            file2: dst2,
        }
    }
'''

# ------------------------------------------------------------------------------
# imports

from crontab import CronTab
import getpass
import os
import shlex
import shutil
import subprocess

# ------------------------------------------------------------------------------
# define the main function to run


def main():

    # --------------------------------------------------------------------------
    # required - DO NOT CHANGE

    # fixed
    curr_user = os.getlogin()
    scpt_user = getpass.getuser()
    home_dir = os.path.expanduser(f'~{curr_user}')
    scpt_dir = os.path.dirname(os.path.abspath(__file__))

    # var
    prog_name = ''
    run_as_root = False
    run_after_install = False
    run_cmd = ''

    # var
    apt_reqs = []
    pip_reqs = []
    create_dirs = []
    create_files = {}
    copy_files = {}

    # print('curr_user:', curr_user)
    # print('scpt_user:', scpt_user)
    # print('home_dir:', home_dir)
    # print('scpt_dir:', scpt_dir)

# ------------------------------------------------------------------------------
# preflight

    prog_name = 'spaceoddity'
    # run_as_root = False  # Default
    run_after_install = True

    conf_dir = os.path.join(home_dir, '.config', prog_name)
    prog_dir = os.path.join(home_dir, f'.{prog_name}')

    run_cmd = os.path.join(prog_dir, f'{prog_name}_main.py')

    apt_reqs = [
        'python3-pip',
        'imagemagick'
    ]
    pip_reqs = [
        'wand'
    ]

    # absolute paths
    create_dirs = [
        conf_dir,
        prog_dir
    ]

    # file name : absolute path
    create_files = {
        f'{prog_name}.log': conf_dir
    }

    # relative file name : absolute path
    copy_files = {
        f'{prog_name}_main.py': prog_dir,
        'LICENSE.txt': prog_dir
    }

    # print('prog_name:', prog_name)
    # print('run_as_root:', run_as_root)
    # print('run_after_install:', run_after_install)
    # print('run_cmd:', run_cmd)
    # print('conf_dir:', conf_dir)
    # print('create_dirs:', create_dirs)
    # print('create_files:', create_files)
    # print('copy_files:', copy_files)

    # # cmd = 'sudo cp spaceoddity_d.py /usr/bin'
    # # subprocess.call(cmd.split())

    # # cmd = 'crontab -e'
    # # subprocess.call(cmd.split())

    # # with open(f'/var/spool/cron/crontabs/{user}'):
    # #     # insert line for spaceoddity
    # #     print()

# ------------------------------------------------------------------------------
# required - DO NOT CHANGE

    if run_as_root and scpt_user != 'root':
        print('This script needs to be run as root. Try \'sudo ./install.py\'')
        exit()
    elif not run_as_root and scpt_user == 'root':
        print('This script should not be run as root. Try \'./install.py\'')
        exit()

    # print('success')
    # exit()

    print(f'Installing {prog_name}...')
    print('For license info see the LICENSE.txt file in this directory')

    print('Installing prerequisites...')
    for item in apt_reqs:
        cmd = f'sudo apt-get install {item}'
        cmd_array = shlex.split(cmd)
        check = subprocess.check_output(cmd_array)
    for item in pip_reqs:
        cmd = f'pip install {item}'
        cmd_array = shlex.split(cmd)
        check = subprocess.check_output(cmd_array)

    print('Creating directories...')
    for item in create_dirs:
        print('making dirs:', item)
        os.makedirs(item, exist_ok=True)

    print('Creating files...')
    for key, val in create_files.items():
        a_path = os.path.join(val, key)
        print('opening:', a_path, 'wb')
        open(a_path, 'wb')

    print('Copying files...')
    for key, val in copy_files.items():
        a_key = os.path.join(scpt_dir, key)
        print('copying:', a_key, val)
        shutil.copy(a_key, val)

    print(f'{prog_name} installed.')

    if run_after_install:
        print(f'Running {prog_name}')
        print("run:", run_cmd)
        run_cmd_array = shlex.split(run_cmd)
        subprocess.call(run_cmd_array)

# ------------------------------------------------------------------------------
# postflight

    # TODO: learn more about this
    # https://pypi.org/project/python-crontab/
    my_cron = CronTab(user=True)

    my_job = None
    for job in my_cron:
        if job.comment == f'{prog_name}':
            my_job = job

    if my_job is None:
        uid = os.getuid()
        my_job = my_cron.new(command=f'env \
        DISPLAY=:0 \
        DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus \
        /usr/bin/python3 \
        {run_cmd}',
                             comment={prog_name})

    my_job.hour.every(1)
    my_job.minute.on(1)
    my_job.every_reboot()

    my_cron.write()


# ------------------------------------------------------------------------------
# Run the main function if we are not an import
if __name__ == '__main__':
    main()

# -)

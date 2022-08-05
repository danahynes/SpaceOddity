#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: install.py                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: cron

#-------------------------------------------------------------------------------
# imports

import getpass
import os
import shutil
import subprocess

# TODO: files and folders created during this session wil have owner/group set
# to root b/c script was called by sudo. NEED TO FIX THIS

#-------------------------------------------------------------------------------
# define the main function to run

def main():

#-------------------------------------------------------------------------------
# required - DO NOT CHANGE

    # fixed
    curr_user = os.getlogin()
    scpt_user = getpass.getuser()
    home_dir = os.path.expanduser(f'~{curr_user}')
    scpt_dir = os.path.dirname(os.path.abspath(__file__))

    # var
    prog_name = ''
    run_as_root = True
    run_after_install = False
    run_cmd = ''

    # var
    create_dirs = []
    create_files = {}
    copy_files = {}

    # print('curr_user:', curr_user)
    # print('scpt_user:', scpt_user)
    # print('home_dir:', home_dir)
    # print('scpt_dir:', scpt_dir)

#-------------------------------------------------------------------------------
# preflight

    prog_name = 'spaceoddity'
    #run_as_root = True # Default
    run_after_install = True
    run_cmd = os.path.join('/usr/bin', f'{prog_name}_d.py')

    conf_dir = os.path.join(home_dir, '.config', prog_name)

    # absolute paths
    create_dirs = [
        conf_dir
    ]

    # file name : absolute path
    create_files = {
        f'{prog_name}.log' : conf_dir
    }

    # relative file name : absolute path
    copy_files = {
        f'{prog_name}_orig.conf' : conf_dir,
        f'{prog_name}.conf' : conf_dir,
        f'{prog_name}_d.py' : '/usr/bin',
        'uninstall.py' : conf_dir
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

#-------------------------------------------------------------------------------
# required - DO NOT CHANGE

    if run_as_root and scpt_user != 'root':
        print('This script needs to be run as root. Try \'sudo ./install.py\'')
        exit(1)
    elif not run_as_root and scpt_user == 'root':
        print ('This script should not be run as root. Try \'./install.py\'')
        exit(1)

    #print('success')
    # exit(0)

    print(f'Installing {prog_name}...')
    print('For license info see the LICENSE.txt file in this directory')

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
        run_cmd_array = run_cmd.split()
        subprocess.call(run_cmd_array)

#-------------------------------------------------------------------------------
# postflight

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
if __name__ == '__main__':
    main()

# -)

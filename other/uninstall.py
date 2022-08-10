
    #!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: uninstall.py                                         /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: cron

#-------------------------------------------------------------------------------
# imports

import os
import shutil
import subprocess

#-------------------------------------------------------------------------------
# define the main function to run

def main():

#-------------------------------------------------------------------------------
# required - DO NOT CHANGE

    prog_name = ''

    delete_dirs = []
    delete_files = {}

    home_dir = os.path.expanduser('~')

#-------------------------------------------------------------------------------
# preflight

    prog_name = 'SpaceOddity'

    conf_dir = os.path.join(home_dir, '.config', prog_name)

    delete_dirs = [
        conf_dir
    ]

    cmd = 'sudo rm /usr/bin/spaceoddity_d.py'
    subprocess.call(cmd.split())

    with open(f'/var/spool/cron/crontabs/{user}'):
        # remove line for spaceoddity
        print()

#-------------------------------------------------------------------------------
# required - DO NOT CHANGE

    print(f'Uninstalling {prog_name}...')

    print('Removing files...')
    for key, val in delete_files.items():
        a_path = os.path.join(val.lower(), key.lower())
        os.remove(a_path.lower())

    print('Removing directories...')
    for a_dir in delete_dirs:
        shutil.rmtree(a_dir.lower())

    print(f'{prog_name} uninstalled.')

#-------------------------------------------------------------------------------
# postflight

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
if __name__ == '__main__':
    main()

# -)

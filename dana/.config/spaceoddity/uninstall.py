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

#-------------------------------------------------------------------------------
# define the main function to run
def main():

#-------------------------------------------------------------------------------
# required - DO NOT CHANGE
    home_dir = os.path.expanduser('~')
    prog_name = ''
    delete_dirs = []
    delete_files = {}

#-------------------------------------------------------------------------------
# optional
    prog_name = 'SpaceOddity'
    conf_dir = os.path.join(home_dir, '.config', prog_name)

    delete_dirs = [
        conf_dir
    ]

#-------------------------------------------------------------------------------
# required - DO NOT CHANGE
    print(f'Uninstalling {prog_name}...')

    print('Removing files...')
    for key, val in delete_files.items():
        a_file = os.path.join(val.lower(), key.lower())
        os.remove(a_file.lower())

    print('Removing directories...')
    for a_dir in delete_dirs:
        shutil.rmtree(a_dir.lower())

    print(f'{prog_name} uninstalled.')

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
if __name__ == '__main__':
    main()

# -)

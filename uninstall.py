#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: uninstall.py                                         /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/13/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# NEXT: less output, only print step name and ... Done
# NEXT: pre/postflight exit codes
# NEXT: load_conf should load vars from json file

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import os
import shlex
import shutil
import subprocess

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class Uninstaller:

    # --------------------------------------------------------------------------
    # Methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Initialize the class
    # --------------------------------------------------------------------------
    def __init__(self):

        # get current user's home dir
        self.home_dir = os.path.expanduser('~')

        # get current dir
        self.src_dir = os.path.dirname(os.path.abspath(__file__))

        # these are the values to set in preflight
        self.run_as_root = False
        self.prog_name = ''

        self.preflight = []
        self.del_files = {}
        self.del_dirs = []
        self.postflight = []

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # set options
        self.__load_conf()

        # check for run as root/need to run as root
        file_name = os.path.basename(__file__)
        run_root = (os.geteuid() == 0)
        if self.run_as_root and not run_root:
            msg = 'This script needs to be run as root. '\
                  f'Try \'sudo ./{file_name}\''
            print(msg)
            exit()
        elif not self.run_as_root and run_root:
            msg = 'This script should not be run as root. '\
                  f'Try \'./{file_name}\''
            print(msg)
            exit()

        # show some text
        print(f'Uninstalling {self.prog_name}')

        # do the steps in order
        self.do_preflight()
        self.do_del_dirs()
        self.do_del_files()
        self.do_postflight()

        # done uninstalling
        print(f'{self.prog_name} uninstalled')

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Run preflight scripts
    # --------------------------------------------------------------------------

    def do_preflight(self):

        # show some text
        print('Running preflight scripts')

        for item in self.preflight:

            # show that we are doing something
            print(f'Running {item}')

            # make relative file into absolute
            abs_item = os.path.join(self.src_dir, item)

            # run item
            cmd = abs_item
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except Exception as error:
                print(f'Could not run {cmd}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Remove any necessary directories
    # --------------------------------------------------------------------------
    def do_del_dirs(self):

        # show some text
        print('Removing directories')

        # for each folder we need to delete
        for item in self.del_dirs:

            # show that we are doing something
            print(f'Removing directory {item}')

            # remove the folder
            try:
                shutil.rmtree(item)
            except Exception as error:

                # not a fatal error
                print(f'Could not remove directory {item}:', error)

    # --------------------------------------------------------------------------
    # Remove any necessary files (outside above directiories)
    # --------------------------------------------------------------------------
    def do_del_files(self):

        # show some text
        print('Removing files')

        # for each file we need to copy
        for key, val in self.del_files.items():

            # convert relative path to absolute path
            abs_key = os.path.join(self.src_dir, key)

            # show that we are doing something
            print(f'Removing file {abs_key}')

            # remove the file (if it'wasn't in a folder above)
            if os.path.exists(abs_key):
                try:
                    os.remove(abs_key)
                except Exception as error:
                    print(f'Could not remove file {abs_key}:', error)

    # --------------------------------------------------------------------------
    # Run postflight scripts
    # --------------------------------------------------------------------------
    def do_postflight(self):

        # show some text
        print('Running postflight scripts')

        for item in self.postflight:

            # show that we are doing something
            print(f'Running {item}')

            # make relative file into absolute
            abs_item = os.path.join(self.src_dir, item)

            # run item
            cmd = abs_item
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except Exception as error:
                print(f'Could not run {cmd}:', error)
                exit()

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Set options from __init__
    # --------------------------------------------------------------------------
    def __load_conf(self):

        # set root required
        self.run_as_root = False  # default

        # the program name
        self.prog_name = 'spaceoddity'

        # preflight scripts
        # NB: these should be relative to src_dir
        self.preflight = [
            # default empty
        ]

        # get some dirs
        dst_dir = os.path.join(self.home_dir, f'.{self.prog_name}')
        cfg_dir = os.path.join(self.home_dir, '.config', f'{self.prog_name}')

        # delete dirs
        # NB: these should be absolute paths
        self.del_dirs = [
            dst_dir,
            cfg_dir
        ]

        # delete files
        # NB: key is relative to src_dir, value is absolute
        self.del_files = {
            # default empty
        }

        # postflight scripts
        # NB: these should be relative to src_dir
        self.postflight = [
            'cron-uninstall.py'
        ]


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    uninstaller = Uninstaller()
    uninstaller.run()

# -)

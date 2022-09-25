#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: install.py                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/13/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# NEXT: take out run_after and run_cmd, make postflight for prog_name
# NEXT: how to check results of apt and pip install
#       use subprocess.call and check result - see main script
# NEXT: less output, only print step name and ... Done
# NEXT: redirect apt and pip to /dev/null to reduce messages
# NEXT: pre/postflight exit codes
#       this means we can use echo -e with ellipsis and Done
# NEXT: make a module with installer/uninstaller
# NEXT: add version string to options and print at start of install
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


class Installer:

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

        # these are the values to set in set_options
        self.run_as_root = False
        self.prog_name = ''

        self.preflight = []
        self.sys_reqs = []
        self.py_reqs = []
        self.make_dirs = []
        self.copy_files = {}
        self.postflight = []

        self.run_after_install = False
        self.run_cmd = ''

        '''
        {
            'run_as_root': 0,
            'prog_name': '',
            'preflight': {
                'script1'       # relative to ${SRC}
            }
            'sys_reqs': {
                'lib1'
            },
            'py_reqs': {
                'lib2'
            },
            'make_dirs': {
                'dir1'          # absolute (use ${HOME})
            },
            'copy_files':{
                'src1': 'dst1'  # src relative to ${SRC}, dst absolute (use ${HOME})
            },
            'postflight': {
                'script2'       # relative
            }
            run_after_install': 0,
            'run_cmd': ''       # absolute
        }

        ${HOME} - user's home dir
        ${SRC} - current dir of install.py
        '''

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
            msg = 'This script needs to be run as root.'
            msg += f'Try \'sudo ./{file_name}\''
            print(msg)
            exit()
        elif not self.run_as_root and run_root:
            msg = 'This script should not be run as root.'
            msg += f'Try \'./{file_name}\''
            print(msg)
            exit()

        # show some text
        print(f'Installing {self.prog_name}')

        # do the steps in order
        self.do_preflight()
        self.do_sys_reqs()
        self.do_py_reqs()
        self.do_make_dirs()
        self.do_copy_files()
        self.do_postflight()

        # done installing
        print(f'{self.prog_name} installed')

        # run the program now
        if self.run_after_install:
            self.run_prog()

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
    # Install system prerequisites
    # --------------------------------------------------------------------------
    def do_sys_reqs(self):

        # show some text
        print('Installing system requirements')

        # show that we are doing something
        print('Installing pip')

        # always install pip
        cmd = 'sudo apt-get install python3-pip'
        cmd_array = shlex.split(cmd)
        try:
            subprocess.run(cmd_array)
        except Exception as error:
            print('Could not install pip:', error)
            exit()

        # get system requirements
        for item in self.sys_reqs:

            # show that we are doing something
            print(f'Installing {item}')

            # install apt reqs
            cmd = f'sudo apt-get install {item}'
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except Exception as error:
                print(f'Could not install {item}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Install python prerequisites
    # --------------------------------------------------------------------------
    def do_py_reqs(self):

        # get python requirements
        for item in self.py_reqs:

            # show that we are doing something
            print(f'Installing {item}')

            # install pip reqs
            cmd = f'pip3 install {item}'
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except Exception as error:
                print(f'Could not install {item}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Make any necessary directories
    # --------------------------------------------------------------------------
    def do_make_dirs(self):

        # show some text
        print('Creating directories')

        # for each folder we need to make
        for item in self.make_dirs:

            # show that we are doing something
            print(f'Making directory {item}')

            # make the folder(s)
            try:
                os.makedirs(item, exist_ok=True)
            except Exception as error:
                print(f'Could not create directory {item}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Copy all files to their dests
    # --------------------------------------------------------------------------
    def do_copy_files(self):

        # show some text
        print('Copying files')

        # for each file we need to copy
        for key, val in self.copy_files.items():

            # show that we are doing something
            print(f'Copying {key} to {val}')

            # convert relative path to absolute path
            abs_key = os.path.join(self.src_dir, key)

            # copy the file
            try:
                shutil.copy(abs_key, val)
            except Exception as error:
                print(f'Could not copy file {abs_key}:', error)
                exit()

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
    # Run the program after install
    # --------------------------------------------------------------------------
    def run_prog(self):

        # show some text
        print(f'Running {self.prog_name}')

        # run program now
        cmd_array = shlex.split(self.run_cmd)
        try:
            subprocess.run(cmd_array)
        except Exception as error:
            print(f'Could not run {self.prog_name}:', error)
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

        # system requirements
        self.sys_reqs = [
            'imagemagick'
        ]

        # python requirements
        self.py_reqs = [
            'wand',
            'python-crontab'
        ]

        # get some dirs
        dst_dir = os.path.join(self.home_dir, f'.{self.prog_name}')
        cfg_dir = os.path.join(self.home_dir, '.config', f'{self.prog_name}')

        # make dirs
        # NB: these should be absolute paths
        self.make_dirs = [
            dst_dir,
            cfg_dir
        ]

        # copy files to dests
        # NB: key is relative to src_dir, value is absolute
        self.copy_files = {
            f'{self.prog_name}.py': dst_dir,
            'uninstall.py': dst_dir,
            'LICENSE': dst_dir,
            'VERSION': dst_dir
        }

        # postflight scripts
        # NB: these should be relative to src_dir
        self.postflight = [
            'cron-install.py'
        ]

        # whether to run after install
        self.run_after_install = True
        # NB: this path should be absolute
        self.run_cmd = os.path.join(dst_dir, f'{self.prog_name}.py')


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    installer = Installer()
    installer.run()

# -)

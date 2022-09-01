#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: install.py                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 08/31/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: i18n strings?

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import getpass
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

        # make sure we are not sudo'ed
        scpt_user = getpass.getuser()
        if scpt_user == 'root':
            print('This script should not be run as root. Try \'./install.py\'')
            exit()

        # the program name
        self.prog_name = 'spaceoddity'

        # get some dirs
        home_dir = os.path.expanduser('~')
        self.prog_dir = os.path.join(home_dir, f'.{self.prog_name}')
        self.inst_dir = os.path.dirname(os.path.abspath(__file__))

        # system requirements
        self.apt_reqs = [
            'python3-pip',
            'imagemagick'
        ]

        # python requirements
        self.pip_reqs = [
            'wand',
            'python-crontab'
        ]

        # make dirs
        self.make_dirs = [
            self.prog_dir
        ]

        # copy files to dests
        # TODO: gonna have to deal with relative paths to abs paths
        # these should be 'rel/to/inst/dir: /rel/to/prog/dir"

        self.copy_files = {
            f'{self.prog_name}_main.py': self.prog_dir,
            'LICENSE':  self.prog_dir,
            'VERSION': self.prog_dir
        }

        # the program to run after install
        self.run_path = os.path.join(self.prog_dir, f'{self.prog_name}_main.py')

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # show some text
        print(f'Installing {self.prog_name}...')
        print('For license info see the LICENSE.txt file in this directory')

        # do the steps in order
        self.__do_reqs()
        self.__make_dirs()
        self.__copy_files()
        self.__do_crontab()

        # done installing
        print(f'{self.prog_name} installed.')

        # run the program now
        self.__run_prog()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Install prerequisites for install
    # --------------------------------------------------------------------------
    def __do_reqs(self):

        # show some text
        print('Installing requirements...')

        # get system requirements
        for item in self.apt_reqs:

            # show that we are doing something
            print(f'Installing {item}...')

            # install apt reqs
            cmd = f'sudo apt-get install {item}'
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except subprocess.CalledProcessError as error:
                print(error.stderr.decode())
                exit()

        # get python requirements
        for item in self.pip_reqs:

            # show that we are doing something
            print(f'Installing {item}...')

            # install pip reqs
            cmd = f'pip install {item}'
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except subprocess.CalledProcessError as error:
                print(error.stderr.decode())
                exit()

    # --------------------------------------------------------------------------
    # Make any necessary directories
    # --------------------------------------------------------------------------
    def __make_dirs(self):

        # show some text
        print('Creating directories...')

        # for each folder we need to make
        for item in self.make_dirs:

            # show that we are doing something
            print(f'Making directory {item}...')

            # make the folder(s)
            os.makedirs(item, exist_ok=True)

    # --------------------------------------------------------------------------
    # Copy all files to their dests
    # --------------------------------------------------------------------------
    def __copy_files(self):

        # show some text
        print('Copying files...')

        # for each file we need to copy
        for key, val in self.copy_files.items():

            # show that we are doing something
            print(f'Copying {key} to {val}...')

            # copy the file
            shutil.copy(key, val)

    # --------------------------------------------------------------------------
    # Set up crontab for changing wallpaper
    # --------------------------------------------------------------------------
    def __do_crontab(self):

        # get crontab library
        from crontab import CronTab

        # show some text
        print('Install crontab job...')

        # TODO: learn more about this
        # https://pypi.org/project/python-crontab/

        # get current user's crontab
        my_cron = CronTab(user=True)

        # find job
        my_job = None
        for job in my_cron:
            if job.comment == f'{self.prog_name}':
                my_job = job

        # create new job if neccesary
        if my_job is None:
            uid = os.getuid()
            my_job = my_cron.new(command=f'env \
            DISPLAY=:0 \
            DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus \
            /usr/bin/python3 \
            {self.run_path}',
                                 comment={self.prog_name})

        # set job parameters
        my_job.hour.every(1)
        my_job.minute.on(1)
        my_job.every_reboot()

        # save job parameters
        my_cron.write()

    # --------------------------------------------------------------------------
    # Run the program after install
    # --------------------------------------------------------------------------
    def __run_prog(self):

        # show some text
        print(f'Running {self.prog_name}...')

        # run program now
        cmd_array = shlex.split(self.run_path)
        try:
            subprocess.run(cmd_array)
        except subprocess.CalledProcessError as error:
            print(error.stderr.decode())
            exit()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    installer = Installer()
    installer.run()

# -)

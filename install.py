#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: install.py                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# NEXT: run at screen unlock
# https://unix.stackexchange.com/questions/28181/how-to-run-a-script-on-screen-lock-unlock
# this means we don't need a cron job, except maybe just after midnight
# also make cron job run every 10 minutes

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import os
import shlex
import shutil
import subprocess

# TODO: an uninstaller that removes cron jobs
# NEXT: run every hour,
# NEXT: check date intead or url

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

        # these are the values to set in preflight
        self.prog_name = ''
        self.run_as_root = False
        self.run_after_install = False

        self.sys_reqs = []
        self.pip_reqs = []
        self.make_dirs = []
        self.copy_files = {}

        self.run_cmd = ''

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # check for run as root/need to run as root
        run_root = (os.geteuid() == 0)
        if self.run_as_root and not run_root:
            msg = 'This script needs to be run as root. '
            msg += 'Try \'sudo ./install.py\''
            print(msg)
            exit()
        elif not self.run_as_root and run_root:
            msg = 'This script should not be run as root. '
            msg += 'Try \'./install.py\''
            print(msg)
            exit()

        # show some text
        print(f'Installing {self.prog_name}')

        # do the steps in order
        self.__do_preflight()
        self.__do_reqs()
        self.__make_dirs()
        self.__copy_files()
        self.__do_postflight()

        # done installing
        print(f'{self.prog_name} installed')

        # run the program now
        if self.run_after_install:
            self.__run_prog()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Preflight - setup all variables from init
    # --------------------------------------------------------------------------

    def __do_preflight(self):

        # the program name
        self.prog_name = 'spaceoddity'

        # set run vars
        # self.run_as_root = False # Default
        self.run_after_install = True

        # system requirements
        self.sys_reqs = [
            'python3-pip',
            'imagemagick'
        ]

        # python requirements
        self.pip_reqs = [
            'wand',
            'python-crontab'
        ]

        # get some dirs
        dst_dir = os.path.join(self.home_dir, f'.{self.prog_name}')
        cfg_dir = os.path.join(self.home_dir, '.config', {self.prog_name})

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
            'LICENSE':  dst_dir,
            'VERSION': dst_dir,
            'README.md': dst_dir
        }

        # the program to run after install
        self.run_cmd = os.path.join(dst_dir, f'{self.prog_name}.py')

    # --------------------------------------------------------------------------
    # Install prerequisites
    # --------------------------------------------------------------------------
    def __do_reqs(self):

        # show some text
        print('Installing requirements')

        # get system requirements
        for item in self.sys_reqs:

            # show that we are doing something
            print(f'Installing {item}')

            # install apt reqs
            cmd = f'sudo apt-get install {item}'
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except subprocess.CalledProcessError as error:
                print(f'Could not install {item}:', error.stderr.decode())
                exit()

        # get python requirements
        for item in self.pip_reqs:

            # show that we are doing something
            print(f'Installing {item}')

            # install pip reqs
            cmd = f'pip install {item}'
            cmd_array = shlex.split(cmd)
            try:
                subprocess.run(cmd_array)
            except subprocess.CalledProcessError as error:
                print(f'Could not install {item}:', error.stderr.decode())
                exit()

    # --------------------------------------------------------------------------
    # Make any necessary directories
    # --------------------------------------------------------------------------
    def __make_dirs(self):

        # show some text
        print('Creating directories')

        # for each folder we need to make
        for item in self.make_dirs:

            # show that we are doing something
            print(f'Making directory {item}')

            # make the folder(s)
            try:
                os.makedirs(item, exist_ok=True)
            except OSError as error:
                print(f'Could not create directory {item}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Copy all files to their dests
    # --------------------------------------------------------------------------
    def __copy_files(self):

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
            except OSError as error:
                print(f'Could not copy file {abs_key}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Set up crontab for changing wallpaper
    # --------------------------------------------------------------------------
    def __do_postflight(self):

        # get crontab library
        from crontab import CronTab

        # show some text
        print('Creating cron job')

        # set the job command
        uid = os.getuid()
        cron_cmd = 'env '
        cron_cmd += 'DISPLAY=:0 '
        cron_cmd += f'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus '
        cron_cmd += '/usr/bin/python3 '
        cron_cmd += f'{self.run_cmd}'

        # get current user's crontab
        my_cron = CronTab(user=True)

        # find 'every' job
        my_job = None
        for job in my_cron:
            if job.comment == f'{self.prog_name} every':
                my_job = job
                my_job.enable()

        # # create new job if neccesary
        if my_job is None:
            my_job = my_cron.new(command=cron_cmd,
                                 comment=f'{self.prog_name} every')
            my_job.minute.every(10)

        # find 'reboot' job
        my_job = None
        for job in my_cron:
            if job.comment == f'{self.prog_name} reboot':
                my_job = job
                my_job.enable()

        # # create new job if neccesary
        if my_job is None:
            my_job = my_cron.new(command=cron_cmd,
                                 comment=f'{self.prog_name} reboot')
            my_job.every_reboot()

        # save job parameters
        my_cron.write()

    # --------------------------------------------------------------------------
    # Run the program after install
    # --------------------------------------------------------------------------
    def __run_prog(self):

        # show some text
        print(f'Running {self.prog_name}')

        # run program now
        cmd_array = shlex.split(self.run_cmd)
        try:
            subprocess.run(cmd_array)
        except subprocess.CalledProcessError as error:
            print(f'Could not run {self.prog_name}:', error.stderr.decode())
            exit()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    installer = Installer()
    installer.run()

# -)

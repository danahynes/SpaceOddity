#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: install-cron.py                                      /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/13/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import os
import shlex
import shutil
import subprocess

# NB: requires:
# python-crontab (pip)

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

        # do the steps in order
        self.__do_preflight()

        # show some text
        # NB: must be done after preflight to get self.prog_name
        print(f'Installing {self.prog_name}')

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
        self.prog_name = f'{self.prog_name}-cron'

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
            except Exception as error:
                print(f'Could not install {item}:', error)
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
            except Exception as error:
                print(f'Could not install {item}:', error)
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
            except Exception as error:
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
            except Exception as error:
                print(f'Could not copy file {abs_key}:', error)
                exit()

    # --------------------------------------------------------------------------
    # Set up crontab for changing wallpaper
    # --------------------------------------------------------------------------
    def __do_postflight(self):

        # import the crontab module
        from crontab import CronTab

        # show some text
        print('Creating cron job')

        # # get some dirs
        dst_dir = os.path.join(self.home_dir, f'.{self.prog_name}')

        # # the program to run after install
        run_cmd = os.path.join(dst_dir, f'{self.prog_name}.py')

        # set the job command
        uid = os.getuid()
        cron_cmd = 'env '
        cron_cmd += 'DISPLAY=:0 '
        cron_cmd += f'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus '
        cron_cmd += '/usr/bin/python3 '
        cron_cmd += f'{run_cmd}'

        # get current user's crontab
        my_cron = CronTab(user=True)

        # find 'every' job
        my_job = None
        for job in my_cron:
            if job.comment == f'{self.prog_name} every':
                my_job = job

        # # create new job if neccesary
        if my_job is None:
            my_job = my_cron.new(command=cron_cmd,
                                 comment=f'{self.prog_name} every')

        # set job time
        my_job.enable()
        my_job.minute.every(10)

        # find 'reboot' job
        my_job = None
        for job in my_cron:
            if job.comment == f'{self.prog_name} reboot':
                my_job = job

        # # create new job if neccesary
        if my_job is None:
            my_job = my_cron.new(command=cron_cmd,
                                 comment=f'{self.prog_name} reboot')

        # set job time
        my_job.enable()
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
        except Exception as error:
            print(f'Could not run {self.prog_name}:', error)
            exit()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    installer = Installer()
    installer.run()

# -)

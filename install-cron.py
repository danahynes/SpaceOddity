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
from crontab import CronTab

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class CronInstaller:

    # --------------------------------------------------------------------------
    # Methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Initialize the class
    # --------------------------------------------------------------------------
    def __init__(self):

        # get current user's home dir
        self.home_dir = os.path.expanduser('~')

        # these are the values to set in preflight
        self.prog_name = ''
        self.run_as_root = False

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # do the steps in order
        self.__do_preflight()

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
        # NB: must be done after preflight to get self.prog_name
        print('Installing cron job')

        self.__do_postflight()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Preflight - setup all variables from init
    # --------------------------------------------------------------------------

    def __do_preflight(self):

        # the program name
        self.prog_name = 'spaceoddity'

        # # get some dirs
        dst_dir = os.path.join(self.home_dir, f'.{self.prog_name}')

        # # the program to run after install
        self.run_cmd = os.path.join(dst_dir, f'{self.prog_name}.py')

    # --------------------------------------------------------------------------
    # Set up crontab for changing wallpaper
    # --------------------------------------------------------------------------
    def __do_postflight(self):

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


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    installer = CronInstaller()
    installer.run()

# -)

#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: cron-install.py                                      /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/23/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from crontab import CronTab
import os

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
        pass

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # show some text
        print('Creating cron job')

        # get prog name
        prog_name = 'spaceoddity'

        # # get some dirs
        home_dir = os.path.expanduser('~')
        dst_dir = os.path.join(home_dir, f'.{prog_name}')

        # # the program to run from cron
        run_cmd = os.path.join(dst_dir, f'{prog_name}.py')

        # set the job command
        # NB: the env is required to futz w/ the screen from cron
        # (which technically runs headless)
        uid = os.getuid()
        cron_cmd = 'env '\
                   'DISPLAY=:0 '\
                   f'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{uid}/bus '\
                   '/usr/bin/python3 '\
                   f'{run_cmd}'

        # get current user's crontab
        my_cron = CronTab(user=True)

        # find 'every' job
        my_job = None
        for job in my_cron:
            if job.comment == f'{prog_name} every':
                my_job = job

        # # create new job if neccesary
        if my_job is None:
            my_job = my_cron.new(command=cron_cmd,
                                 comment=f'{prog_name} every')

        # set job time
        my_job.enable()
        my_job.minute.every(10)

        # find 'reboot' job
        my_job = None
        for job in my_cron:
            if job.comment == f'{prog_name} reboot':
                my_job = job

        # # create new job if neccesary
        if my_job is None:
            my_job = my_cron.new(command=cron_cmd,
                                 comment=f'{prog_name} reboot')

        # set job time
        my_job.enable()
        my_job.every_reboot()

        # save job parameters
        my_cron.write()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    installer = Installer()
    installer.run()

# -)

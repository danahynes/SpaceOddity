#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: uninstall.py                                         /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/13/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import os
import shutil

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

        # these are the values to set in preflight
        self.prog_name = ''
        self.run_as_root = False

        self.del_dirs = []

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # check for run as root/need to run as root
        run_root = (os.geteuid() == 0)
        if self.run_as_root and not run_root:
            msg = 'This script needs to be run as root. '
            msg += 'Try \'sudo ./uninstall.py\''
            print(msg)
            exit()
        elif not self.run_as_root and run_root:
            msg = 'This script should not be run as root. '
            msg += 'Try \'./uninstall.py\''
            print(msg)
            exit()

        # do the steps in order
        self.__do_preflight()

        # show some text
        # NB: must be done after preflight to get self.prog_name
        print(f'Uninstalling {self.prog_name}')

        # self.__do_reqs()
        self.__del_dirs()
        self.__do_postflight()

        # done uninstalling
        print(f'{self.prog_name} uninstalled')

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Preflight - setup all variables from init
    # --------------------------------------------------------------------------

    def __do_preflight(self):

        # the program name
        self.prog_name = 'spaceoddity'

        # get some dirs
        dst_dir = os.path.join(self.home_dir, f'.{self.prog_name}')
        cfg_dir = os.path.join(self.home_dir, '.config', f'{self.prog_name}')

        # make dirs
        # NB: these should be absolute paths
        self.del_dirs = [
            dst_dir,
            cfg_dir
        ]

    # --------------------------------------------------------------------------
    # Remove any necessary directories
    # --------------------------------------------------------------------------
    def __del_dirs(self):

        # show some text
        print('Removing directories')

        # for each folder we need to make
        for item in self.del_dirs:

            # show that we are doing something
            print(f'Removing directory {item}')

            # remove the folder(s)
            try:
                shutil.rmtree(item)
            except Exception as error:
                print(f'Could not remove directory {item}:', error)

    # --------------------------------------------------------------------------
    # Remove crontab for changing wallpaper
    # --------------------------------------------------------------------------
    def __do_postflight(self):

        # get crontab library
        from crontab import CronTab

        # show some text
        print('Removing cron job')

        # get current user's crontab
        my_cron = CronTab(user=True)

        # remove 'every' job
        for job in my_cron:
            if job.comment == f'{self.prog_name} every':
                my_cron.remove(job)

        # remove 'reboot' job
        for job in my_cron:
            if job.comment == f'{self.prog_name} reboot':
                my_cron.remove(job)

        # save job parameters
        my_cron.write()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    uninstaller = Uninstaller()
    uninstaller.run()

# -)

#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: cron-uninstall.py                                    /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/24/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from crontab import CronTab

# NB: requires:
# python-crontab (pip)

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class Cron_Uninstaller:

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
        print('Deleting cron job')

        # get prog name
        prog_name = 'spaceoddity'

        # get current user's crontab
        my_cron = CronTab(user=True)

        # remove 'every' job
        for job in my_cron:
            if job.comment == prog_name:
                my_cron.remove(job)

        # save job parameters
        my_cron.write()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    uninstaller = Cron_Uninstaller()
    uninstaller.run()

# -)

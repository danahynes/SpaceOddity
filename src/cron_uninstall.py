# ------------------------------------------------------------------------------
# Project : SpaceOddity                                            /          \
# Filename: cron_uninstall.py                                     |     ()     |
# Date    : 09/24/2022                                            |            |
# Author  : Dana Hynes                                            |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from crontab import CronTab

# NB: requires:
# python-crontab (pip)


# --------------------------------------------------------------------------
# Methods
# --------------------------------------------------------------------------

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
# This happens when we run script from install.py
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    run()

# -)

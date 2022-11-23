# ------------------------------------------------------------------------------
# Project : SpaceOddity                                            /          \
# Filename: cron_install.py                                       |     ()     |
# Date    : 09/23/2022                                            |            |
# Author  : cyclopticnerve                                        |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from crontab import CronTab
import os

# NB: requires:
# python-crontab (pip)


# --------------------------------------------------------------------------
# Methods
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Run the script
# --------------------------------------------------------------------------
def run():

    '''
        installs program into crontab
    '''

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
    # NB: the env stuff is required to futz w/ the screen from cron
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
        if job.comment == prog_name:
            my_job = job

    # # create new job if neccesary
    if my_job is None:
        my_job = my_cron.new(command=cron_cmd, comment=prog_name)

    # set job time
    my_job.enable()
    my_job.minute.every(10)

    # save job parameters
    my_cron.write()


# ------------------------------------------------------------------------------
# Run this script as if we are not an import
# This happens when we run script from install.py
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    run()

# -)

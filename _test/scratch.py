import os
from crontab import CronTab

curr_user = os.getlogin()

my_cron = CronTab(user=curr_user)

found = False
for job in my_cron:
    if job.comment == 'spaceoddity':
        found = True
        job.hour.every(1)
        job.minute.on(1)

if not found:
    job = my_cron.new(command='env \
    DISPLAY=:0 \
    DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
    /usr/bin/python3 \
    /home/dana/Documents/Projects/SpaceOddity/spaceoddity_main.py',
                      comment='spaceoddity')

    job.hour.every(2)

my_cron.write()

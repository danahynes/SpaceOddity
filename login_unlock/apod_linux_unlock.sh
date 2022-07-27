#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: apod_linux_unlock.sh                                 /          \  #
# Project : APOD_Linux                                          |     ()     | #
# Date    : 02/21/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# watch dbus for unlock event
gdbus monitor --system --dest org.freedesktop.login1 |
{
  while read LINE
  do

    # search line for keyword and return number of matches (-c: count matches)
    COUNT=$(echo "${LINE}" | grep -c "Session.Unlock")

    # if we found keyword
    if [ "${COUNT}" == "1" ]
    then

      # let the log know whats up
      echo "Unlock" >> "${HOME}/.apod_linux/apod_linux.log"

      # do the thing now (at unlock)
      # NB: we fork it so this loop doesn't get stuck waiting for the
      # sleep in the python script - on the off chance we get two unlock
      # events within the sleep time (sleeping doesn't stop the script -
      # only a logout or reboot will stop it)
      python3 /usr/bin/apod_linux.py & disown
    fi
  done
}

# -)

#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: uninstall.sh                                         /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

PROG_NAME="SpaceOddity"

# show some progress
# NB: first call with sudo to ask for password on its own line (aesthetics)
sudo echo "Uninstalling ${PROG_NAME}..."

# stop the unlock listener
# echo -n "Stopping unlock listener... "
# sudo pkill -f "/usr/bin/apod_linux_unlock.sh"
# echo "Done"

# set the hidden dir where we will store our junk
INSTALL_DIR="${HOME}/.config/${PROG_NAME}"

# delete dirs/files from locations
echo -n "Deleting data directory... "
sudo rm -rf "${INSTALL_DIR}"
echo "Done"

# delete the scripts from their locations (needs admin hence sudo)
echo -n "Deleting scripts from their locations..."
# sudo rm -f "/usr/bin/apod_linux_caption.sh"
# sudo rm -f "/usr/bin/apod_linux_unlock.sh"
# sudo rm -f "/usr/bin/apod_linux.py"
# sudo rm -f "/etc/profile.d/apod_linux_login.sh"
echo "Done"

# delete gui
# echo -n "Deleting GUI... "
# sudo rm -f "/usr/bin/apod_linux_config.py"
# sudo rm -f "${HOME}/.local/share/applications/apod_linux.desktop"
# sudo rm -f "/usr/share/icons/hicolor/128x128/apps/apod_linux_icon.png"
# echo "Done"

# show that we are done
echo "${PROG_NAME} uninstalled"

# -)

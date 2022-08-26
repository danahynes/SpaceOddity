#!/usr/bin/env bash
#------------------------------------------------------------------------------#
# Filename: install.sh                                           /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: sources to final places
# TODO: dependencies

PROG_NAME="SpaceOddity"

# make sure we are installing as user (not root or sudo)
# USER=$(whoami)
# if [ "${USER}" == "root" ]
# then
#   echo "Do not run as root or with sudo"
#   exit 1
# fi

# show some progress
# NB: first call with sudo to ask for password on its own line (aesthetics)
sudo echo "Installing ${PROG_NAME}..."
echo "For license info see the LICENSE.txt file in this directory"

# # stop the unlock listener (so we don't run it twice)
# echo -n "Stopping unlock listener... "
# sudo pkill -f "/usr/bin/apod_linux_unlock.sh"
# echo "Done"

# set the hidden dir where we will store our junk
CONFIG_DIR="${HOME}/.config/${PROG_NAME}"

# make the dir to store user data
echo -n "Creating config directory... "
mkdir -p "${CONFIG_DIR}"
echo "Done"

# install the conf file (as user)
echo -n "Copying config file... "
cp "./${PROG_NAME}_orig.conf" "${CONFIG_DIR}"
cp "./${PROG_NAME}.conf" "${CONFIG_DIR}"
echo "Done"

# install the uninstaller
echo -n "Copying uninstaller... "
cp "./uninstall.sh" "${INSTALL_DIR}"
echo "Done"

# make a log file now in case anyone needs it before the py script runs (the py
# logging system will create the file if needed, but bash scripts won't)
echo -n "Creating log file... "
touch "${INSTALL_DIR}/${PROG_NAME}.log"
echo "Done"

# copy the scripts to their locations (needs admin hence sudo)
echo -n "Copying scripts to their locations... "
# sudo cp "./apod_linux_caption.sh" "/usr/bin"
# sudo cp "./apod_linux_unlock.sh" "/usr/bin"
# sudo cp "./apod_linux.py" "/usr/bin"
# sudo cp "./apod_linux_login.sh" "/etc/profile.d"
echo "Done"

# install gui
# echo -n "Installing GUI... "
# sudo cp "./gui/apod_linux_config.py" "/usr/bin"
# cp "./gui/apod_linux.desktop" "${HOME}/.local/share/applications"
# sudo cp "./gui/apod_linux_icon.png" "/usr/share/icons/hicolor/128x128/apps"
# sudo update-icon-caches "/usr/share/icons/*"
# sudo gtk-update-icon-cache
# echo "Done"

# run the script now (as user) (fork and release as child)
echo -n "Running ${PROG_NAME} now... "
# /etc/profile.d/apod_linux_login.sh
echo "Done"

# show that we are done
echo "${PROG_NAME} installed"

# -)

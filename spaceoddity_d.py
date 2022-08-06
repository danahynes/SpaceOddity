#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_d.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: break this into discrete functions
# TODO: maybe clear log between runs? only save last?
# TODO: check hdurl against prev, if same, bail
# TODO: set wallpaper name with new date/time and delete old (avoids 'replace'
# dialog)
# does this explain why deleting the file from ~/.config/spaceoddity
# causes wallpaper to go black and not get replaced on next run?
# also note right-clicking a file in nautilus and selecting "set as wallpaper"
# copies the file to ~/Pictures/Wallpapers and maybe deletes other files?
# b/c now i lost my orange stripey bg
# basically weird shit happens when you delete the spaceoddity_desk.{file_ext}
# file... needs further testing

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import json
import logging
import os
import subprocess
import urllib.request

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

DEBUG = 1

#-------------------------------------------------------------------------------
# Define the main function
#-------------------------------------------------------------------------------

def main():

#-------------------------------------------------------------------------------
# Initialize
#-------------------------------------------------------------------------------

    prog_name = 'spaceoddity'
    script_path = os.path.dirname(os.path.realpath(__file__))

    # get locations
    home_dir = os.path.expanduser('~')
    conf_dir = os.path.join(home_dir, '.config', prog_name)
    data_file = os.path.join(conf_dir, f'{prog_name}.dat')
    log_file = os.path.join(conf_dir, f'{prog_name}.log')
    conf_file = os.path.join(conf_dir, f'{prog_name}.json')
    cap_path = os.path.join(script_path, f'./{prog_name}_c.py')

    # create folders/files if they do not exist
    if not os.path.exists(conf_dir):
        os.mkdir(conf_dir)
    if not os.path.exists(log_file):
        with open(log_file, 'w+', encoding = 'utf-8') as file:
            file.write('')
    if not os.path.exists(conf_file):
        with open(conf_file, 'w+', encoding = 'utf-8') as file:
            file.write('{}')

    # set up logging
    logging.basicConfig(filename = log_file, level = logging.DEBUG,
        format = '%(asctime)s - %(message)s')

    # log start
    logging.debug('------------------------------------------------------')
    logging.debug('Starting main script')

    if DEBUG:
        print('home_dir:', home_dir)
        print('conf_dir:', conf_dir)
        print('data_file:', data_file)
        print('log_file:', log_file)
        print('conf_file:', conf_file)
        print('cap_path:', cap_path)

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    # set defaults
    config_defaults = {
        'enabled' : 1,
        'caption' : 1
    }

    # read config file
    with open(conf_file, encoding = 'UTF-8') as file:
        config = json.load(file)

    # get values or defaults
    for key in config_defaults:
        if not key in config.keys():
            config[key] = config_defaults.get(key)

    if DEBUG:
        print('config:', config)

    # the only keys we care about
    enabled = bool(config['enabled'])
    caption = bool(config['caption'])

#-------------------------------------------------------------------------------
# Bail if not enabled
#-------------------------------------------------------------------------------

    if not enabled:
        logging.debug('Not enabled')
        exit(0)

#-------------------------------------------------------------------------------
# Get JSON from api.nasa.gov
#-------------------------------------------------------------------------------

    # the url to load JSON from
    apod_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

    # get the JSON and format it
    try:

        # get json from url
        response = urllib.request.urlopen(apod_url)
        json_data = response.read()
        apod_data = json.loads(json_data)

        # save json data to file (for use by caption script)
        with open(data_file, 'w', encoding = 'UTF-8') as file:
            json.dump(apod_data, file, ensure_ascii = False, indent = 4)

        logging.debug('Got JSON from server')

        if DEBUG:
            print('apod_data:', apod_data)

    except urllib.error.URLError as err:
        logging.debug('Could not get JSON')
        logging.debug(err)

        if DEBUG:
            print('error:', err)

        exit(1)

#-------------------------------------------------------------------------------
# Get pic from api.nasa.gov
#-------------------------------------------------------------------------------

    # make sure it's an image (sometimes it's a video)
    media_type = apod_data['media_type']
    if 'image' in media_type:

        # get the url to the actual image
        pic_url = apod_data['hdurl']

        file_ext = pic_url.split('.')[-1]
        pic_name = f'{prog_name}_desk.{file_ext}'
        pic_path = os.path.join(conf_dir, pic_name)

        if DEBUG:
            print('pic_url:', pic_url)
            print('file_ext:', file_ext)
            print('pic_name:', pic_name)
            print('pic_path:', pic_path)

        try:

            # download the full picture
            urllib.request.urlretrieve(pic_url, pic_path)
            logging.debug('Downloaded new file')
        except urllib.error.URLError as err:
            logging.debug('Could not get new file')
            logging.debug(err)

            if DEBUG:
                print('error:', err)

            exit(1)
    else:
        logging.debug('Not an image, doing nothing')
        exit(0)

        # NB: this is for testing on days when the APOD is not an image
        # pic_path = os.path.join(home_dir,
        # 'Documents/Projects/APOD_Linux/test.jpg')
        # apod_data = {'explanation':'Lorem ipsum dolor sit amet, consectetur
        # adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
        # magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
        # ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute
        # irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
        # fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident,
        # sunt in culpa qui officia deserunt mollit anim id est laborum.'

#-------------------------------------------------------------------------------
# Run caption script
#-------------------------------------------------------------------------------

    if caption:
        logging.debug('Running caption script')

        # set cmd for running caption
        cmd = cap_path
        cmd_array = cmd.split()
        subprocess.call(cmd_array)

    else:
        logging.debug('No caption')

#-------------------------------------------------------------------------------
# Set the wallpaper
#-------------------------------------------------------------------------------

    # set cmd for Gnome wallpaper and run
    cmd = f'gsettings set org.gnome.desktop.background picture-uri \
        {pic_path}'
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    # set cmd for Gnome dark wallpaper and run
    cmd = f'gsettings set org.gnome.desktop.background picture-uri-dark \
        {pic_path}'
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    logging.debug('pic is set')

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

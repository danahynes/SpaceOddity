#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_d.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# imports
import configparser
import json
import logging
import os
import subprocess
import urllib.request

# NB: this script assumes that
# ~/.config/spaceoddity/ exists, as well as
# ~/.config/spaceoddity/spaceoddity.log and
# ~/.config/spaceoddity/spaceoddity.conf

#-------------------------------------------------------------------------------
# Define the main function
#-------------------------------------------------------------------------------

def main():

#-------------------------------------------------------------------------------
# Initialize
#-------------------------------------------------------------------------------

    prog_name = 'spaceoddity'

    # get locations
    home_dir = os.path.expanduser('~')
    conf_dir = os.path.join(home_dir, '.config', prog_name)
    log_file = os.path.join(conf_dir, f'{prog_name}.log')
    conf_file = os.path.join(conf_dir, f'{prog_name}.conf')
    # cap_path = f'/usr/bin/{prog_name}_caption.sh'

    # set up logging
    logging.basicConfig(filename = log_file, level = logging.DEBUG,
        format = '%(asctime)s - %(message)s')

    # print('home_dir:', home_dir)
    # print('conf_dir:', conf_dir)
    # print('log_file:', log_file)
    # print('conf_file:', conf_file)
    # print('cap_path:', cap_path)
    # exit(0)

#-------------------------------------------------------------------------------
# Start script and set default config values
#-------------------------------------------------------------------------------

    # log start
    logging.debug('-----------------------------------------------------------')
    logging.debug('Starting script')

    # defaults
    enabled = True
    caption = False

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    config_parser = configparser.ConfigParser()
    config_parser.read(conf_file)
    config = config_parser[f'{prog_name}']

    enabled = config['enabled']
    enabled = bool(int(enabled))

    caption = config['caption']
    caption = bool(int(caption))

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
        logging.debug('Got JSON from server')
    except urllib.error.URLError as err:
        logging.debug('Could not get JSON')
        logging.debug(err)
        exit(1)

#-------------------------------------------------------------------------------
# Get pic from api.nasa.gov
#-------------------------------------------------------------------------------

    # make sure it's an image (sometimes it's a video)
    media_type = apod_data['media_type']
    if 'image' in media_type:

        # get the url to the actual image
        pic_url = apod_data['hdurl']

        # create a download file path
        file_ext = pic_url.split('.')[-1]
        pic_name = f'{prog_name}_wallpaper.{file_ext}'
        pic_path = os.path.join(conf_dir, pic_name)

        try:

            # download the full picture
            urllib.request.urlretrieve(pic_url, pic_path)
            logging.debug('Downloaded new file')
        except urllib.error.URLError as err:
            logging.debug('Could not get new file')
            logging.debug(err)
            exit(1)
    else:
        logging.debug('Not an image, doing nothing')

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

        exit(0)

#-------------------------------------------------------------------------------
# Run caption script
#-------------------------------------------------------------------------------
    if not caption:
        logging.debug('No caption')
    else:
        title = apod_data['title']
        text = apod_data['explanation']

        print('title:', title)
        print('text:', text)

    # if we have a valid pic_path
    # if pic_path is not None and caption:
    #     try:

    #         # get text to send
    #         cap_text = apod_data['explanation']

    #         # call the caption script with text and pic path
    #         subprocess.call([cap_path, pic_path, cap_text])

    #     except OSError as e:
    #         logging.debug(str(e))
    #         sys.exit(1)



#-------------------------------------------------------------------------------
# Set wallpaper using final pic
#-------------------------------------------------------------------------------

    # set cmd for Gnome wallpaper and run
    cmd = 'gsettings set org.gnome.desktop.background picture-uri ' + \
        pic_path
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    # set cmd for Gnome dark wallpaper and run
    cmd = 'gsettings set org.gnome.desktop.background picture-uri-dark ' + \
        pic_path
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    logging.debug('pic is set')

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

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
    conf_file = os.path.join(conf_dir, f'{prog_name}.conf')
    # cap_path = f'/usr/bin/{prog_name}_caption.sh'
    log_file = os.path.join(conf_dir, f'{prog_name}.log')

    # set up logging
    logging.basicConfig(filename = log_file, level = logging.DEBUG,
        format = '%(asctime)s - %(message)s')

    # print('home_dir:', home_dir)
    # print('conf_dir:', conf_dir)
    # print('conf_file:', conf_file)
    # print('cap_path:', cap_path)
    # print('log_file:', log_file)
    # exit(0)

#-------------------------------------------------------------------------------
# Prevent more than one instance running at a time (to avoid file collisions)
#-------------------------------------------------------------------------------

    # get lock file (write-only, create if necessary)
    # lock_file = os.open(f'/tmp/' + prog_name + '.lock',
    #         os.O_WRONLY | os.O_CREAT)

    # # check for existance of lock file
    # try:
    #     fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    #     already_running = False
    # except IOError:
    #     already_running = True

    # # another instance is running, log and exit normally
    # if already_running:
    #     logging.debug('Already running')
    #     sys.exit(0)

#-------------------------------------------------------------------------------
# Start script and set default config values
#-------------------------------------------------------------------------------

    # log start
    logging.debug('-----------------------------------------------------------')
    logging.debug('Starting script')

    # defaults
    enabled = True
    # delay = 30
    # caption = True

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    config = configparser.ConfigParser()
    config.read(conf_file)
    config_section = f'{prog_name}'

    # for section in config.sections():
    #     print('section:', section)

    #     for key in config[section]:
    #         print('key:', key, ', val:', config[section][key])

    enabled = config[config_section]['enabled']
    enabled = bool(int(enabled))

            # print()

        # for key in config[section]:

    #     if section == f'{prog_name}':
    #         for key in config[section]:
    #             val = config[section][key]

    #             if key.lower() == 'enabled':
    #                 enabled = int(val)
    #                 print('enabled:', bool(enabled))

    #                 if not enabled:
    #                     logging.debug('Not enabled')
    #                     exit(0)

    # try:

    #     if os.path.exists(conf_file):
    #         with open(conf_file, 'r') as f:
    #             lines = f.readlines()

    #             # read key/value pairs from conf file
    #             for line in lines:
    #                 line_clean = line.strip().upper()

    #                 # ignore comment lines or blanks or lines with no values
    #                 if line_clean.startswith('#') or line_clean == '':
    #                     continue

    #                 # split key off at equals
    #                 key_val = line_clean.split('=')
    #                 key = key_val[0].strip()

    #                 # split val off ignoring trailing comments
    #                 val = ''
    #                 if (len(key_val) > 1):
    #                     val_array = key_val[1].split('#')
    #                     val = val_array[0].strip()

    #                 # check if we are enabled
    #                 if key == 'ENABLED':
    #                     if val != '':
    #                         enabled = int(val)

    #                 # get delay
    #                 if key == 'DELAY':
    #                     if val != '':
    #                         delay = int(val)

    #                 # get caption
    #                 if key == 'CAPTION':
    #                     if val != '':
    #                         caption = int(val)

    # except Exception as e:
    #     logging.debug(str(e))

#-------------------------------------------------------------------------------
# Bail if not enabled
#-------------------------------------------------------------------------------

    if not enabled:
        logging.debug('Not enabled')
        exit(0)

    # # wait for internet to come up
    # # NB: the scripts apod_linux_login.sh and apod_linux_unlock.sh fork this
    # # script, so a sleep here does not hang the login/unlock process
    # time.sleep(delay)

#-------------------------------------------------------------------------------
# Get JSON from api.nasa.gov
#-------------------------------------------------------------------------------

    # the url to load JSON from
    apod_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

    # get the JSON and format it
    try:

        # get json from url
        response = urllib.request.urlopen(apod_url)
        byte_data = response.read()
        apod_data = json.loads(byte_data)
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
        # pic_path is conf_dir + pic_name
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

    # if we have a valid pic_path
    # if pic_path is not None:
    #     try:

    #         # first check for env varible
    #         a_dir = os.getenv('XDG_GREETER_DATA_DIR')
    #         if a_dir is not None:
    #             logging.debug('No greeter dir, bailing')
    #             sys.exit(1)

    #         # get location of script
    #         cmd = '/usr/lib/x86_64-linux-gnu/io.elementary.contract.set-wallpaper'

    #         # call the script with pic path
    #         subprocess.call([cmd, pic_path])

    #         # remove file since its been copied everywhere
    #         # NB: this is kept with eOS specific code since we know that's how
    #         # set-wallpaper works. other os's may need to keep the file in place
    #         os.remove(pic_path)
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

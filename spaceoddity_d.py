#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_d.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: test all conditions (no internet, bad url, etc)
# TODO: maybe clear log between runs? only save last? filemaode='w'
# TODO: check hdurl against prev, if same, bail (NO! this will break gui apply -
# maybe only re-run caption stuff instead of re-downloading file? how much
# would that save?)
# TODO: set wallpaper name with new date/time and delete old (avoids 'replace'
# dialog) maybe not necessary
# does this explain why deleting the file from ~/.config/spaceoddity
# causes wallpaper to go black and not get replaced on next run?
# also note right-clicking a file in nautilus and selecting "set as wallpaper"
# copies the file to ~/Pictures/Wallpapers and maybe deletes other files?
# b/c now i lost my orange stripey bg
# basically weird shit happens when you delete the spaceoddity_desk.{file_ext}
# file... needs further testing

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import json
import logging
import os
import subprocess
import urllib.request

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

DEBUG = 1

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class Main:

    # --------------------------------------------------------------------------
    # Methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Initialize the class
    # --------------------------------------------------------------------------
    def __init__(self):

        self.prog_name = 'spaceoddity'

        # the url to load JSON from
        self.apod_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

        # TODO: make this the final location pf the caption script
        script_path = os.path.dirname(os.path.realpath(__file__))

        # get locations
        home_dir = os.path.expanduser('~')
        self.conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.data_file = os.path.join(self.conf_dir, f'{self.prog_name}.dat')
        log_file = os.path.join(self.conf_dir, f'{self.prog_name}.log')
        self.conf_file = os.path.join(self.conf_dir, f'{self.prog_name}.json')
        cap_path = os.path.join(script_path, f'{self.prog_name}_c.py')

        # create folders/files if they do not exist
        if not os.path.exists(self.conf_dir):
            os.mkdir(self.conf_dir)
        if not os.path.exists(log_file):
            with open(log_file, 'w+') as file:
                file.write('')
        if not os.path.exists(self.conf_file):
            with open(self.conf_file, 'w+') as file:
                file.write('{}')

        if DEBUG:
            print('home_dir:', home_dir)
            print('conf_dir:', self.conf_dir)
            print('data_file:', self.data_file)
            print('log_file:', log_file)
            print('conf_file:', self.conf_file)
            print('cap_path:', cap_path)

        # set up logging
        logging.basicConfig(filename=log_file, level=logging.DEBUG,
                            format='%(asctime)s - %(message)s')

        # log start
        logging.debug('-------------------------------------------------------')
        logging.debug('starting main script')

        # set default config dict
        self.config_defaults = {
            'enabled':      1,
            'show_caption': 1
        }

        # user config dict
        self.config = {}

        # init the config dict from user settings
        self.__load_config()

        # check to see if we are enabled
        if not self.config['enabled']:

            # log that we are finished with script
            self.__exit('not enabled', 0)

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        self.__get_data()
        self.__download_image()

        self.__set_image()

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def __exit(self, msg, code=0):

        # log that we are finished with script
        logging.debug('%s, exiting', msg)
        logging.debug('-------------------------------------------------------')

        # quit script
        exit(code)

    # --------------------------------------------------------------------------
    # Loads the config dict from a file
    # --------------------------------------------------------------------------
    def __load_config(self):

        # read config file
        with open(self.conf_file, 'r') as file:
            try:
                self.config = json.load(file)
                logging.debug('load config file: %s', file)
            except json.JSONDecodeError as err:
                self.config = dict(self.config_defaults)
                logging.debug('could not load json, loading defaults')
                logging.debug(err)

                if DEBUG:
                    print('error:', err)

        # get values or defaults
        for key in self.config_defaults:
            if key not in self.config.keys():
                self.config[key] = self.config_defaults.get(key)

        if DEBUG:
            print('load config:', self.config)

    # --------------------------------------------------------------------------
    # Get sJSON from api.nasa.gov
    # --------------------------------------------------------------------------
    def __get_data(self):

        # get the JSON and format it
        try:

            # get json from url
            response = urllib.request.urlopen(self.apod_url)
            json_data = response.read()
            self.apod_data = json.loads(json_data)

            # save json data to file (for use by caption script)
            with open(self.data_file, 'w+') as file:
                json.dump(self.apod_data, file, indent=4)

            logging.debug('got json from server')

            if DEBUG:
                print('apod_data:', self.apod_data)

        except urllib.error.URLError as err:
            logging.debug(err)

            if DEBUG:
                print('error:', err)

            self.__exit('could not get json', 1)

    # --------------------------------------------------------------------------
    # Get pic from api.nasa.gov
    # --------------------------------------------------------------------------
    def __download_image(self):

        # make sure it's an image (sometimes it's a video)
        media_type = self.apod_data['media_type']
        if 'image' in media_type:

            # get the url to the actual image
            pic_url = self.apod_data['hdurl']

            # create a download path
            file_ext = pic_url.split('.')[-1]
            pic_name = f'{self.prog_name}_desk.{file_ext}'
            self.pic_path = os.path.join(self.conf_dir, pic_name)

            if DEBUG:
                print('pic_url:', pic_url)
                print('file_ext:', file_ext)
                print('pic_name:', pic_name)
                print('pic_path:', self.pic_path)

            try:

                # download the full picture
                urllib.request.urlretrieve(pic_url, self.pic_path)

                logging.debug('downloaded new file')
            except urllib.error.URLError as err:
                logging.debug(err)

                if DEBUG:
                    print('error:', err)

                self.__exit('could not download new file', 1)
        else:

            if DEBUG:
                print('not an image')

            self.__exit('not an image', 0)

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

    # --------------------------------------------------------------------------
    # Run caption script
    # --------------------------------------------------------------------------

        # if show_caption:
        #     logging.debug('run caption script')

        #     # set cmd for running caption
        #     cmd = cap_path
        #     cmd_array = cmd.split()
        #     subprocess.call(cmd_array)

        # else:
        #     logging.debug('caption not enabled')

    # --------------------------------------------------------------------------
    # Set the wallpaper
    # --------------------------------------------------------------------------
    def __set_image(self):

        # set cmd for Gnome wallpaper and run
        cmd = f'gsettings set org.gnome.desktop.background picture-uri \
            {self.pic_path}'
        cmd_array = cmd.split()
        subprocess.call(cmd_array)

        # set cmd for Gnome dark wallpaper and run
        cmd = f'gsettings set org.gnome.desktop.background picture-uri-dark \
            {self.pic_path}'
        cmd_array = cmd.split()
        subprocess.call(cmd_array)

        logging.debug('wallpaper is set')

        if DEBUG:
            print('wallpaper is set')


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main = Main()
    main.run()

# -)

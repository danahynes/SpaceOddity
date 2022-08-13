#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_d.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: test all conditions (no internet, bad url, etc)
# no conf dir:
# No log file:
# No json:
# not enabled:
# Bad json:
# bad url:
# no internet:
# not image:
# bad hdurl:
# caption no:
# caption yes:

# TODO: white line on right of image (oversizing doesn't help)
# TODO: remove all DEBUG

# TODO: add option to span multiple monitors
# I know more-or-less HOW to do this, but as i don't have multiple monitors,
# and I haven't taken the time to fix my laptop's 'HDMI out' connection to my
# TV... I don't have a way to test it. So for now it's on the back burner.

# NB: requires:
# pygobject

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from datetime import datetime
import json
import logging
import os
import shlex
import subprocess
import urllib.request

import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio, GLib  # noqa: E402 (ignore import order)

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

DEBUG = 1
TEST_IMAGE = 1

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

        # set the program name for use in file and folder names
        self.prog_name = 'spaceoddity'

        # the url to load json from
        self.apod_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

        # TODO: make this the final location pf the caption script
        # actually, move caption stuff to this file?
        script_path = os.path.dirname(os.path.realpath(__file__))

        # get locations
        home_path = os.path.expanduser('~')
        self.conf_path = os.path.join(home_path, '.config', self.prog_name)
        self.apod_file = os.path.join(self.conf_path, f'{self.prog_name}.dat')
        log_file = os.path.join(self.conf_path, f'{self.prog_name}.log')
        self.conf_file = os.path.join(self.conf_path, f'{self.prog_name}.cfg')
        self.capt_path = os.path.join(script_path, f'{self.prog_name}_c.py')
        self.capt_file = os.path.join(self.conf_path, f'{self.prog_name}_capt.cfg')

        # create folder if it does not exist
        if not os.path.exists(self.conf_path):
            os.mkdir(self.conf_path)

        if DEBUG:
            print('prog_anme:', self.prog_name)
            print('apod_url:', self.apod_url)
            print('home_path:', home_path)
            print('conf_dir:', self.conf_path)
            print('data_file:', self.apod_file)
            print('log_file:', log_file)
            print('conf_file:', self.conf_file)
            print('capt_path:', self.capt_path)
            print('capt_file:', self.capt_file)

        # set up logging
        logging.basicConfig(filename=log_file, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # log start
        logging.debug('=======================================================')
        logging.debug('start main script')

        # set default config dict
        self.conf_dict_def = {
            'enabled':          1,
            'show_caption':     1,
            'show_title':       1,
            'show_copyright':   1,
            'show_text':        1,
            'position':         8,
            'fg_r':             1.0,
            'fg_g':             1.0,
            'fg_b':             1.0,
            'fg_a':             100,
            'bg_r':             0.0,
            'bg_g':             0.0,
            'bg_b':             0.0,
            'bg_a':             75,
            'caption_width':    500,
            'font_size':        15,
            'corner_radius':    15,
            'border_padding':   20,
            'top_padding':      50,
            'bottom_padding':   10,
            'side_padding':     10
        }

        # user config dict
        self.conf_dict = {}

        # init the config dict from user settings
        self.__load_conf_dict()

        # check to see if we are enabled
        if not self.conf_dict['enabled']:

            # log the enabled state
            logging.debug('main script disabled')

            if DEBUG:
                print('main script disabled')

            # we are finished with script
            self.__exit()

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # call each step in the process
        self.__download_apod_dict()
        self.__download_image()
        self.__resize_image()
        self.__load_capt_dict()
        # self.__do_caption()
        self.__set_image()

        # exit gracefully n
        self.__exit()

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def __exit(self):

        # log that we are finished with script
        logging.debug('exit main script')
        logging.debug('-------------------------------------------------------')

        if DEBUG:
            print('exit main script')

        # quit script
        exit()

    # --------------------------------------------------------------------------
    # Load the config dict from a file
    # --------------------------------------------------------------------------
    def __load_conf_dict(self):

        # if config file does not exist, set defaults and save to file
        if not os.path.exists(self.conf_file):
            self.conf_dict = dict(self.conf_dict_def)
            self.__save_conf_dict()

        # read config file
        with open(self.conf_file, 'r') as file:
            try:
                self.conf_dict = json.load(file)

                # log success
                logging.debug('load config file: %s', self.conf_file)

            except json.JSONDecodeError as error:

                # if config file error, set defaults and save to file
                self.conf_dict = dict(self.conf_dict_def)
                self.__save_conf_dict()

                # log error
                logging.error(error.reason)
                logging.error('could not load config file, load defaults')

                if DEBUG:
                    print('could not load config file, load defaults:',
                          error.reason)

        # set defaults for any missing keys
        for key in self.conf_dict_def:
            if key not in self.conf_dict.keys():
                self.conf_dict[key] = self.conf_dict_def[key]
        self.__save_conf_dict()
        
        if DEBUG:
            print('load config:', self.conf_dict)

    # --------------------------------------------------------------------------
    # Save the user config dict to a file
    # --------------------------------------------------------------------------
    def __save_conf_dict(self):

        # open the file and write json
        with open(self.conf_file, 'w') as file:
            json.dump(self.conf_dict, file, indent=4)

        # log success
        logging.debug('save config file: %s', self.conf_file)

        if DEBUG:
            print('save config:', self.conf_dict)

    # --------------------------------------------------------------------------
    # Get json from caption data file
    # --------------------------------------------------------------------------
    def __load_capt_dict(self):

        # create file if not exist
        if not os.path.exists(self.capt_file):
            self.capt_dict = {}
            self.__save_capt_dict()

        # load dict from file
        with open(self.capt_file, 'r') as file:
            try:
                self.capt_dict = json.load(file)

                # log success
                logging.debug('load capt file: %s', self.capt_file)

            except json.JSONDecodeError as error:

                # if capt file error, set defaults and save to file
                self.capt_dict = {}
                self.__save_capt_dict()

                # log error
                logging.error(error.reason)
                logging.error('could not load capt file')

                if DEBUG:
                    print('could not load capt file:', error.reason)

                # this is a fatal error
                self.__exit()

        if DEBUG:
            print('load capt:', self.capt_dict)

    # --------------------------------------------------------------------------
    # Set capt settings to caption data file
    # --------------------------------------------------------------------------
    def __save_capt_dict(self):

        # open the file and write json
        with open(self.capt_file, 'w') as file:
            json.dump(self.capt_dict, file, indent=4)

        # log success
        logging.debug('save capt file: %s', self.capt_file)

        if DEBUG:
            print('save capt:', self.capt_dict)

    # --------------------------------------------------------------------------
    # Get json from APOD url
    # --------------------------------------------------------------------------
    def __download_apod_dict(self):

        # get the json and format it
        try:

            # get json from url
            response = urllib.request.urlopen(self.apod_url)
            response_text = response.read()
            self.apod_dict = json.loads(response_text)

            # save json data to file (for use by caption script)
            with open(self.apod_file, 'w') as file:
                json.dump(self.apod_dict, file, indent=4)

            # log success
            logging.debug('get data from server')

            if DEBUG:
                print('get data from server:', self.apod_dict)

        except urllib.error.URLError as error:

            # log error
            logging.error(error.reason)
            logging.error('could not get data from server')

            if DEBUG:
                print('could not get data from server:', error.reason)

            # this is a fatal error
            self.__exit()

    # --------------------------------------------------------------------------
    # Set some fake data when debugging and APOD is not an image
    # --------------------------------------------------------------------------
    def __do_not_image(self):

        if TEST_IMAGE:
            print('not an image, making fake data')

            # NB: this is for testing on days when the APOD is not an image
            str_exp = 'Lorem ipsum dolor sit amet, consectetur adipiscing '
            str_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
            str_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
            str_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
            str_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
            str_exp += 'dolor in reprehenderit in voluptate velit esse '
            str_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
            str_exp += 'sint occaecat cupidatat non proident, sunt in '
            str_exp += 'culpa qui officia deserunt mollit anim id est '
            str_exp += 'laborum.'

            self.apod_dict = {
                'title': 'Dummy Title',
                'copyright': 'Dummy Copyright',
                'explanation': f'{str_exp}'
            }

            with open(self.apod_file, 'w') as file:
                json.dump(self.apod_dict, file, indent=4)

            src = '/home/dana/Documents/Projects/SpaceOddity/test/test.jpg'
            dst = '/home/dana/.config/spaceoddity/test.jpg'
            os.system(f'cp {src} {dst}')

            # TODO: move to own function and error check
            self.capt_dict['filepath'] = f'{dst}'
            with open(self.capt_file, 'w') as file:
                json.dump(self.capt_dict, file, indent=4)

        else:

            # log status of apod
            logging.debug('today\'s APOD is not an image')

            # this is a fatal error
            self.__exit()

    # --------------------------------------------------------------------------
    # Get image from api.nasa.gov
    # --------------------------------------------------------------------------
    def __download_image(self):

        # make sure it's an image (sometimes it's a video)
        media_type = self.apod_dict['media_type']
        if 'image' in media_type:

            # get the url to the actual image
            pic_url = ''
            if 'hdurl' in self.apod_dict.keys():
                pic_url = self.apod_dict['hdurl']
            elif 'url' in self.apod_dict.keys():
                pic_url = self.apod_dict['url']

            # bail if no url
            if pic_url == '':

                # log error
                logging.error('no url')

                if DEBUG:
                    print('no url')

                # this is a fatal error
                self.__exit()

            # create a download path
            now = datetime.now()
            str_now = now.strftime('%Y%m%d%H%M%S')
            file_ext = pic_url.split('.')[-1]
            pic_name = f'{self.prog_name}_{str_now}.{file_ext}'
            self.pic_path = os.path.join(self.conf_path, pic_name)

            if DEBUG:
                print('pic_url:', pic_url)
                print('pic_name:', pic_name)
                print('pic_path:', self.pic_path)

            # try to download image
            try:

                # download the hi-res image
                urllib.request.urlretrieve(pic_url, self.pic_path)

                # TODO: remove old file
                # run capt dict functions
                # self.__load_capt_dict()

                # log success
                logging.debug('download image')

            except urllib.error.URLError as error:

                # log error
                logging.error(error.reason)
                logging.error('could not download image')

                if DEBUG:
                    print('could not download image:', error.reason)

                # this is a fatal error
                self.__exit()
        else:

            # do the not image stuff
            self.__do_not_image()

    # --------------------------------------------------------------------------
    # Resize image to fill screen
    # --------------------------------------------------------------------------
    def __resize_image(self):

        # get original size
        cmd = \
            f'identify \
            -format \
            %[fx:w] \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        res = subprocess.check_output(cmd_array)
        old_w = int(res.decode('UTF-8'))

        cmd = \
            f'identify \
            -format \
            %[fx:h] \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        res = subprocess.check_output(cmd_array)
        old_h = int(res.decode('UTF-8'))

        if DEBUG:
            print('pic_w:', old_w)
            print('pic_h:', old_h)

        # get screen size
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        screen_w = geometry.width
        screen_h = geometry.height

        if DEBUG:
            print('screen_w:', screen_w)
            print('screen_h:', screen_h)

        # get the scale factor for height and width
        scale_w = old_w / screen_w
        scale_h = old_h / screen_h

        if DEBUG:
            print('scale_w:', scale_w)
            print('scale_h:', scale_h)

        # use the smallest scale to get the biggest new dimension
        scale = scale_w if scale_w < scale_h else scale_h

        # get the scaled height/width and make sure it still fills the screen
        # after rounding with an int cast
        new_w = int(old_w / scale)
        new_w = screen_w if new_w < screen_w else new_w
        new_h = int(old_h / scale)
        new_h = screen_h if new_h < screen_h else new_h

        if DEBUG:
            print('new_w:', new_w)
            print('new_h:', new_h)

        # do the resize
        cmd = \
            f'convert \
            {self.pic_path} \
            -resize {new_w}x{new_h} \
            -extent {new_w}x{new_h} \
            -gravity center \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # save all the data to a file for caption script
        self.capt_dict['filepath'] = self.pic_path
        self.capt_dict['pic_w'] = new_w
        self.capt_dict['pic_h'] = new_h
        self.capt_dict['screen_w'] = screen_w
        self.capt_dict['screen_h'] = screen_h

        # TODO: move to own function and error check
        with open(self.capt_file, 'w') as file:
            json.dump(self.capt_dict, file, indent=4)

        # log success
        logging.debug('resize image')

    # --------------------------------------------------------------------------
    # Run caption script
    # --------------------------------------------------------------------------
    def __do_caption(self):

        # set cmd for running caption
        cmd = self.capt_path
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

    # --------------------------------------------------------------------------
    # Set the wallpaper
    # --------------------------------------------------------------------------
    def __set_image(self):

        # get system settings
        # settings = Gio.Settings.new('org.gnome.desktop.background')

        # # convert pic_path to variant
        # glib_value = GLib.Variant('s', self.pic_path)

        # # set variant for both light and dark themes
        # settings.set_value('picture-uri', glib_value)
        # settings.set_value('picture-uri-dark', glib_value)

        cmd = f'gsettings set org.gnome.desktop.background picture-uri file://{self.pic_path}'
        cmd_array = cmd.split()
        subprocess.call(cmd_array)
        logging.debug(cmd_array)

        cmd = f'gsettings set org.gnome.desktop.background picture-uri-dark file://{self.pic_path}'
        cmd_array = cmd.split()
        subprocess.call(cmd_array)
        logging.debug(cmd_array)
        # logging.debug(res)

        # log success
        logging.debug('set image')

        if DEBUG:
            print('set image')


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main = Main()
    main.run()

# -)

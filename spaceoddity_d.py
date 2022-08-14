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

# TODO reduce number of f''
# TODO: convert imagemagick calls to wand
# TODO: combine config, apod, capt into single file
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
        curr_dir = os.path.dirname(os.path.realpath(__file__))

        # get locations
        home_dir = os.path.expanduser('~')
        self.conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.conf_path = os.path.join(self.conf_dir, f'{self.prog_name}.cfg')
        self.apod_path = os.path.join(self.conf_dir, f'{self.prog_name}.dat')
        self.capt_path = os.path.join(self.conf_dir,
                                      f'{self.prog_name}_capt.cfg')
        self.scpt_path = os.path.join(curr_dir, f'{self.prog_name}_c.py')
        log_file = os.path.join(self.conf_dir, f'{self.prog_name}.log')

        # create folder if it does not exist
        if not os.path.exists(self.conf_dir):
            os.mkdir(self.conf_dir)

        if DEBUG:
            print('prog_name:', self.prog_name)
            print('apod_url:', self.apod_url)
            print('curr_dir:', curr_dir)
            print('home_dir:', home_dir)
            print('conf_dir:', self.conf_dir)
            print('conf_path:', self.conf_path)
            print('apod_path:', self.apod_path)
            print('capt_path:', self.capt_path)
            print('scpt_path:', self.scpt_path)
            print('log_file:', log_file)

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
        self.conf_dict = {}

        self.apod_dict_def = {
            'media_type':   '',
            'hdurl':        '',
            'url':          '',
            'title':        '',
            'copyrgight':   '',
            'explanation':  ''
        }
        self.apod_dict = {}

        self.capt_dict_def = {
            'filepath': '',
            'pic_w':    0,
            'pic_h':    0,
            'screen_w': 0,
            'screen_h': 0
        }
        self.capt_dict = {}

        self.pic_path = ''

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # init the config dict from user settings
        self.conf_dict = self.__load_dict(self.conf_path,
                                          defaults=self.conf_dict_def)

        # check to see if we are enabled
        if self.conf_dict['enabled']:

            # call each step in the process
            self.__download_apod_dict()
            self.__download_image()
            self.__resize_image()

            # if self.conf_dict['show_caption']:
            # TODO: self.__make_caption()

            self.__set_image()

        else:

            # log the enabled state
            logging.debug('main script disabled')

            if DEBUG:
                print('main script disabled')

        # exit gracefully
        self.__exit()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

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

            # set defaults for any missing keys
            for key in self.apod_dict_def:
                if key not in self.apod_dict.keys():
                    self.apod_dict[key] = self.apod_dict_def[key]

            # log success
            logging.debug('get data from server')

            if DEBUG:
                print('get data from server:', self.apod_dict)

        except urllib.error.URLError as error:

            # if config file error, set defaults and save to file
            self.apod_dict = self.apod_dict_def.copy()

            # log error
            logging.error(error.reason)
            logging.error('could not get data from server')

            if DEBUG:
                print('could not get data from server:', error.reason)

        # save json data to file (for use by caption script)
        self.__save_dict(self.apod_path, self.apod_dict)

    # --------------------------------------------------------------------------
    # Get image from api.nasa.gov
    # --------------------------------------------------------------------------
    def __download_image(self):

        # make sure it's an image (sometimes it's a video)
        media_type = self.apod_dict['media_type']
        if 'image' in media_type:

            # do the image stuff
            self.__apod_is_image()
        else:

            # do the not image stuff
            self.__apod_is_not_image()

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
            print('old_w:', old_w)
            print('old_h:', old_h)

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

        # save the caption data
        self.__save_dict(self.capt_path, self.capt_dict)

        # log success
        logging.debug('resize image')

    # --------------------------------------------------------------------------
    # Run caption script
    # --------------------------------------------------------------------------
    def __make_caption(self):

        # set cmd for running caption
        cmd = self.scpt_path
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

    # --------------------------------------------------------------------------
    # Set the wallpaper
    # --------------------------------------------------------------------------
    def __set_image(self):

        # get system settings
        settings = Gio.Settings.new('org.gnome.desktop.background')

        # convert pic_path to variant
        glib_value = GLib.Variant('s', self.pic_path)

        # set variant for both light and dark themes
        settings.set_value('picture-uri', glib_value)
        settings.set_value('picture-uri-dark', glib_value)

        # cmd = \
        #     f'gsettings \
        #     set \
        #     org.gnome.desktop.background \
        #     picture-uri \
        #     file://{self.pic_path}'
        # cmd_array = shlex.split(cmd)
        # subprocess.call(cmd_array)

        # cmd = \
        #     f'gsettings \
        #     set \
        #     org.gnome.desktop.background \
        #     picture-uri-dark \
        #     file://{self.pic_path}'
        # cmd_array = shlex.split(cmd)
        # subprocess.call(cmd_array)

        # log success
        logging.debug('set image')

        if DEBUG:
            print('set image')

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
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Load dictionary data from a file
    # --------------------------------------------------------------------------
    def __load_dict(self, filepath, defaults=None):

        # create a local dictionary to hold result
        dictionary = {}

        # if config file does not exist, set defaults and save to file
        if not os.path.exists(filepath):
            if defaults is not None:
                dictionary = defaults.copy()
            self.__save_dict(filepath, dictionary)

        # read config file
        with open(filepath, 'r') as file:
            try:
                dictionary = json.load(file)

                # set defaults for any missing keys
                if defaults is not None:
                    for key in defaults:
                        if key not in dictionary.keys():
                            dictionary[key] = defaults[key]

                # log success
                logging.debug('load dict file: %s', filepath)

                if DEBUG:
                    print('load dict:', dictionary)

            except json.JSONDecodeError as error:

                # if config file error, set defaults and save to file
                if defaults is not None:
                    dictionary = defaults.copy()

                # log error
                logging.error(error.reason)
                logging.error('could not load config file, load defaults')

                if DEBUG:
                    print('could not load config file, load defaults:',
                          error.reason)

        # save the dict either way
        self.__save_dict(filepath, dictionary)

        # and send it back
        return dictionary

    # --------------------------------------------------------------------------
    # Save dioctionary data to a file
    # --------------------------------------------------------------------------
    def __save_dict(self, filepath, dictionary):

        # open the file and write json
        with open(filepath, 'w') as file:
            json.dump(dictionary, file, indent=4)

        # log success
        logging.debug('save dict file: %s', filepath)

        if DEBUG:
            print('save dict:', dictionary)

    # --------------------------------------------------------------------------
    # Get the image when it isi an actual image
    # --------------------------------------------------------------------------
    def __apod_is_image(self):

        # get the url to the actual image
        pic_url = self.__get_pic_url()

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
        self.pic_path = os.path.join(self.conf_dir, pic_name)

        if DEBUG:
            print('pic_url:', pic_url)
            print('pic_name:', pic_name)
            print('pic_path:', self.pic_path)

        # try to download image
        try:

            # download the hi-res image
            urllib.request.urlretrieve(pic_url, self.pic_path)

            # remove old file
            self.capt_dict = self.__load_dict(self.capt_path,
                                              defaults=self.capt_dict_def)
            old_path = self.capt_dict['filepath']
            if os.path.exists(old_path):
                os.remove(old_path)

            # log success
            logging.debug('download image')

            if DEBUG:
                print('download image')

        except urllib.error.URLError as error:

            # log error
            logging.error(error.reason)
            logging.error('could not download image')

            if DEBUG:
                print('could not download image:', error.reason)

            # this is a fatal error
            self.__exit()

    # --------------------------------------------------------------------------
    # Set some fake data when debugging and APOD is not an image
    # --------------------------------------------------------------------------
    def __apod_is_not_image(self):

        # NB: HOLY SHIRTBALLS THIS IS AN UGLY HACK!!!
        # but I can't afford to go 24 hours without testing

        if TEST_IMAGE:
            print('not an image, making fake data')

            # NB: this is for testing on days when the APOD is not an image
            fake_url = '/home/dana/Documents/Projects/SpaceOddity/static/test.jpg'
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
                'media_type':   'image',
                'hdurl':        f'{fake_url}',
                'url':          f'{fake_url}',
                'title':        'Dummy Title',
                'copyright':    'Dummy Copyright',
                'explanation':  f'{str_exp}'
            }

            # save the fake apod data
            self.__save_dict(self.apod_path, self.apod_dict)
            self.apod_dict = self.__load_dict(self.apod_path,
                                              self.apod_dict_def)

            # get the url to the actual image
            pic_url = self.__get_pic_url()

            # create a download path
            now = datetime.now()
            str_now = now.strftime('%Y%m%d%H%M%S')
            file_ext = pic_url.split('.')[-1]
            pic_name = f'{self.prog_name}_{str_now}.{file_ext}'
            self.pic_path = os.path.join(self.conf_dir, pic_name)

            if DEBUG:
                print('pic_url:', pic_url)
                print('pic_name:', pic_name)
                print('pic_path:', self.pic_path)

            # copy test image (simulates downloading)
            os.system(f'cp {pic_url} {self.pic_path}')

            # remove old file
            self.capt_dict = self.__load_dict(self.capt_path,
                                              defaults=self.capt_dict_def)
            old_path = self.capt_dict['filepath']
            if os.path.exists(old_path):
                os.remove(old_path)

    # --------------------------------------------------------------------------
    # Get the most appropriate url to the full size image
    # --------------------------------------------------------------------------
    def __get_pic_url(self):

        pic_url = ''
        if 'hdurl' in self.apod_dict.keys():
            pic_url = self.apod_dict['hdurl']
        elif 'url' in self.apod_dict.keys():
            pic_url = self.apod_dict['url']

        return pic_url


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main = Main()
    main.run()

# -)

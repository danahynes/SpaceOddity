#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_d.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/17/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: test all conditions (no internet, bad url, etc)
# no conf dir:OK
# No log file: OK
# No cfg:OK
# bad cfg: OK
# not enabled: OK
# bad apod url: OK
# no internet: OK
# not image: OK
# bad pic url: OK
# caption no: OK
# caption yes:

# TODO: white line on right of image (oversizing doesn't help)
# TODO: remove all DEBUG
# TODO: some imagemagick python binding

# NB: requires:
# pygobject
# imagemagick

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

        # get locations
        home_dir = os.path.expanduser('~')
        self.conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.conf_path = os.path.join(self.conf_dir, f'{self.prog_name}.cfg')
        log_path = os.path.join(self.conf_dir, f'{self.prog_name}.log')

        # create folder if it does not exist
        if not os.path.exists(self.conf_dir):
            os.mkdir(self.conf_dir)

        # set up logging
        logging.basicConfig(filename=log_path, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # log start
        logging.debug('=======================================================')
        logging.debug('start main script')

        # set default config dict
        self.conf_dict_def = {
            'options': {
                'enabled':          1,
                'show_caption':     1,
                'show_title':       1,
                'show_copyright':   1,
                'show_text':        1,
                'position':         8,
                'fg_r':             1.0,
                'fg_g':             1.0,
                'fg_b':             1.0,
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
            },
            'apod': {
                'media_type':       '',
                'hdurl':            '',
                'url':              '',
                'title':            '',
                'copyright':        '',
                'explanation':      ''
            },
            'caption': {
                'old_filepath':     '',
                'filepath':         '',
                'pic_w':            0,
                'pic_h':            0,
                'screen_w':         0,
                'screen_h':         0
            },
        }

        # user config dict
        self.conf_dict = {}

        # path to final image
        self.pic_path = ''

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # init the config dict from user settings
        self.__load_conf()

        # check to see if we are enabled
        options = self.conf_dict['options']
        if options['enabled']:

            # call each step in the process
            self.__download_apod_dict()
            self.__download_image()
            self.__resize_image()

            if options['show_caption']:
                self.__make_caption()

            self.__set_image()

        else:

            # log the enabled state
            logging.debug('main script disabled')

        # exit gracefully
        self.__exit()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Get json from APOD url
    # --------------------------------------------------------------------------
    def __download_apod_dict(self):

        # the url to load json from
        apod_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

        # get the json and format it
        try:

            # get json from url
            response = urllib.request.urlopen(apod_url)
            response_text = response.read()
            apod_dict = json.loads(response_text)

            # set defaults for any missing keys
            apod_dict_def = self.conf_dict_def['apod']
            for key in apod_dict_def:
                if key not in apod_dict.keys():
                    apod_dict[key] = apod_dict_def[key]

            # apply new dict to config
            self.conf_dict['apod'] = apod_dict

            # log success
            logging.debug('get data from server')

            # save json data to file (for use by caption script)
            self.__save_conf()

        except urllib.error.URLError as error:

            # log error
            logging.error(error.reason)
            logging.error('could not get data from server')

            # this is a fatal error
            self.__exit()

    # --------------------------------------------------------------------------
    # Get image from api.nasa.gov
    # --------------------------------------------------------------------------
    def __download_image(self):

        # make sure it's an image (sometimes it's a video)
        apod_dict = self.conf_dict['apod']
        media_type = apod_dict['media_type']
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

        # get original width
        cmd = \
            f'identify \
            -format %w \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        out = subprocess.check_output(cmd_array)
        old_w = int(out)

        # get original height
        cmd = \
            f'identify \
            -format %h \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        out = subprocess.check_output(cmd_array)
        old_h = int(out)

        # get screen size
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        screen_w = geometry.width
        screen_h = geometry.height

        # get the scale factor for height and width
        scale_w = old_w / screen_w
        scale_h = old_h / screen_h

        # use the smallest scale to get the biggest new dimension
        scale = scale_w if scale_w < scale_h else scale_h

        # get the scaled height/width and make sure it still fills the screen
        # after rounding with an int cast
        new_w = int(old_w / scale)
        new_w = screen_w if new_w < screen_w else new_w
        new_h = int(old_h / scale)
        new_h = screen_h if new_h < screen_h else new_h

        cmd = \
            f'convert \
            {self.pic_path} \
            -resize {new_w}x{new_h} \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # save all the data to a file for caption script
        capt_dict = self.conf_dict['caption']
        capt_dict['filepath'] = self.pic_path
        capt_dict['pic_w'] = new_w
        capt_dict['pic_h'] = new_h
        capt_dict['screen_w'] = screen_w
        capt_dict['screen_h'] = screen_h

        # log success
        logging.debug('resize image')

        # save the caption data
        self.__save_conf()

    # --------------------------------------------------------------------------
    # Run caption script
    # --------------------------------------------------------------------------
    def __make_caption(self):

        # TODO: make this the final location pf the caption script
        # actually, move caption stuff to this file?
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        scpt_path = os.path.join(curr_dir, f'{self.prog_name}_caption.py')

        # set cmd for running caption
        cmd = scpt_path
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

        # remove old file
        capt_dict = self.conf_dict['caption']
        old_path = capt_dict['old_filepath']
        if os.path.exists(old_path):
            os.remove(old_path)

        # move new file to old file
        capt_dict['old_filepath'] = capt_dict['filepath']
        capt_dict['filepath'] = self.pic_path
        self.__save_conf()

        # log success
        logging.debug('set image')

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def __exit(self):

        # log that we are finished with script
        logging.debug('exit main script')
        logging.debug('-------------------------------------------------------')

        # quit script
        exit()

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Load dictionary data from a file
    # --------------------------------------------------------------------------
    def __load_conf(self):

        # if config file does not exist, set defaults and save to file
        if not os.path.exists(self.conf_path):
            self.conf_dict = self.conf_dict_def.copy()
            self.__save_conf()

        # read config file
        with open(self.conf_path, 'r') as file:
            try:
                self.conf_dict = json.load(file)

                # set defaults for any missing keys
                for key in self.conf_dict_def:
                    if key not in self.conf_dict.keys():
                        self.conf_dict[key] = self.conf_dict_def[key]

                # log success
                logging.debug('load conf file: %s', self.conf_path)

            except json.JSONDecodeError as error:

                # if config file error, set defaults and save to file
                self.conf_dict = self.conf_dict_def.copy()

                # log error
                logging.error(error)
                logging.error('could not load config file, load defaults')

        # save the dict either way
        self.__save_conf()

    # --------------------------------------------------------------------------
    # Save dioctionary data to a file
    # --------------------------------------------------------------------------
    def __save_conf(self):

        # open the file and write json
        with open(self.conf_path, 'w') as file:
            json.dump(self.conf_dict, file, indent=4)

        # log success
        logging.debug('save conf file: %s', self.conf_path)

    # --------------------------------------------------------------------------
    # Get the image when it isi an actual image
    # --------------------------------------------------------------------------
    def __apod_is_image(self):

        # get the url to the actual image
        pic_url = self.__get_pic_url()

        # create a download path
        now = datetime.now()
        str_now = now.strftime('%Y%m%d%H%M%S')
        file_ext = pic_url.split('.')[-1]
        pic_name = f'{self.prog_name}_{str_now}.{file_ext}'
        self.pic_path = os.path.join(self.conf_dir, pic_name)

        # try to download image
        try:

            # download the hi-res image
            urllib.request.urlretrieve(pic_url, self.pic_path)

            # log success
            logging.debug('download image')

        except ValueError as error:

            # log error
            logging.error(error)
            logging.error('could not download image')

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
            fake_url = '/home/dana/Documents/Projects/SpaceOddity/static/'
            fake_url += 'test.jpg'
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

            apod_dict = self.conf_dict['apod']
            apod_dict['media_type'] = 'image'
            apod_dict['hdurl'] = fake_url
            apod_dict['url'] = fake_url
            apod_dict['title'] = 'Dummy Title'
            apod_dict['copyright'] = 'Dummy Copyright'
            apod_dict['explanation'] = str_exp

            # save the fake apod data
            self.__save_conf()

            # get the url to the actual image
            pic_url = self.__get_pic_url()

            # create a download path
            now = datetime.now()
            str_now = now.strftime('%Y%m%d%H%M%S')
            file_ext = pic_url.split('.')[-1]
            pic_name = f'{self.prog_name}_{str_now}.{file_ext}'
            self.pic_path = os.path.join(self.conf_dir, pic_name)

            # copy test image (simulates downloading)
            os.system(f'cp {pic_url} {self.pic_path}')

            # log success
            logging.debug('make fake image')

    # --------------------------------------------------------------------------
    # Get the most appropriate url to the full size image
    # --------------------------------------------------------------------------
    def __get_pic_url(self):

        pic_url = ''
        apod_dict = self.conf_dict['apod']
        if 'hdurl' in apod_dict.keys():
            pic_url = apod_dict['hdurl']
        elif 'url' in apod_dict.keys():
            pic_url = apod_dict['url']

        return pic_url


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main = Main()
    main.run()

# -)

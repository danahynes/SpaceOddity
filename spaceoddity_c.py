#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_c.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: test all options
# TODO: check for title/copyright/expl and any other data in apod_data
# also better formatting if one or more not preset
# qlso test with empty strings
# TODO: redirect all imagemagick errors to log file
# TODO: convert imagemagick calls to wand

# TODO: remove DEBUG

# NB: requires :
# imagemagick (sudo apt install imagemagick)
# wand (pip install wand)
# pygobject

# NB: this script assumes that
# ~/.config/spaceoddity/ exists, as well as
# ~/.config/spaceodlogging.debug('dity/spaceoddity.dat
# ~/.config/spaceoddity/spaceoddity_desk.???,
# ~/.config/spaceoddity/spaceoddity.json,
# ~/.config/spaceoddity/spaceoddity.log,

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import json
import logging
import os
import shlex
import subprocess

# TODO: remove after getting info from file
import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk  # noqa: E402 (ignore import order)

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

DEBUG = 1

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class Caption:

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
        self.data_file = os.path.join(self.conf_dir, f'{self.prog_name}.dat')
        log_file = os.path.join(self.conf_dir, f'{self.prog_name}.log')
        self.conf_file = os.path.join(self.conf_dir, f'{self.prog_name}.cfg')
        self.capt_file = os.path.join(self.conf_dir, f'{self.prog_name}_capt.cfg')

        if DEBUG:
            print('home_dir:', home_dir)
            print('conf_dir:', self.conf_dir)
            print('data_file:', self.data_file)
            print('log_file:', log_file)
            print('conf_file:', self.conf_file)
            print('capt_file:', self.capt_file)

        # set up logging
        logging.basicConfig(filename=log_file, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # log start
        logging.debug('-------------------------------------------------------')
        logging.debug('start caption script')

        # set defaults
        self.config_defaults = {
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
        self.config = {}

        # init the config dict from user settings
        self.__load_config()

        # check to see if we are enabled
        if not self.config['show_caption']:

            # log the caption state
            logging.debug('caption script disabled')

            if DEBUG:
                print('caption script disabled')

            # we are finished with script
            self.__exit()

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # call each step in the process
        self.__get_data()
        self.__make_caption()
        self.__combine_images()

        # exit gracefully
        self.__exit()

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def __exit(self):

        # log that we are finished with script
        logging.debug('exit caption script',)
        logging.debug('-------------------------------------------------------')

        if DEBUG:
            print('exit caption script')

        # quit script
        exit()

    # --------------------------------------------------------------------------
    # Load the config dict from a file
    # --------------------------------------------------------------------------
    def __load_config(self):

        # make sure conf file exists
        if not os.path.exists(self.conf_file):
            self.config = dict(self.config_defaults)
            self.__save_config()

        # read config file
        with open(self.conf_file, 'r') as file:
            try:
                self.config = json.load(file)

                # log success
                logging.debug('load config file: %s', self.conf_file)

            except json.JSONDecodeError as error:

                # shallow copy defaults to user
                self.config = dict(self.config_defaults)

                # log error
                logging.error(error.reason)
                logging.error('could not load config file, load defaults')

                # save the defualt config
                self.__save_config()

                if DEBUG:
                    print('could not load config file, load defaults:',
                          error.reason)

        # set defaults for any missing keys
        for key in self.config_defaults:
            if key not in self.config.keys():
                self.config[key] = self.config_defaults.get(key)

        if DEBUG:
            print('load config:', self.config)

    # --------------------------------------------------------------------------
    # Save the user config dict to a file
    # --------------------------------------------------------------------------
    def __save_config(self):

        # open the file and write json
        with open(self.conf_file, 'w') as file:
            json.dump(self.config, file, indent=4)

        # log success
        logging.debug('save config file: %s', self.conf_file)

        if DEBUG:
            print('save config:', self.config)

    # --------------------------------------------------------------------------
    # Get data file (the apod data downloaded by main script)
    # --------------------------------------------------------------------------
    def __get_data(self):

        # TODO: error check load json

        # open data file
        with open(self.data_file, 'r') as file:
            apod_data = json.load(file)

        # get data for caption
        str_title = ''
        if 'title' in apod_data.keys():
            str_title = apod_data['title']
        str_copy = ''
        if 'copyright' in apod_data.keys():
            str_copy = apod_data['copyright']
        str_text = ''
        if 'explanation' in apod_data.keys():
            str_text = apod_data['explanation']

        if DEBUG:
            print('str_title:', str_title)
            print('str_copy:', str_copy)
            print('str_text:', str_text)

        # form a string from shown attributes
        self.str_caption = ''
        if self.config['show_title'] and str_title != '':
            self.str_caption += str_title + '\n\n'
        if self.config['show_copyright'] and str_copy != '':
            self.str_caption += str_copy + '\n\n'
        if self.config['show_text'] and str_text != '':
            self.str_caption += str_text

        # NB: limit on cqption is ~1000 cahracters
        self.str_caption = self.str_caption[:1000]

        if DEBUG:
            print('str_caption:', self.str_caption)

        # log success
        logging.debug('get data from dat file')

    # --------------------------------------------------------------------------
    # Make caption png
    # --------------------------------------------------------------------------
    def __make_caption(self):

        # remove border size for text-only png
        self.caption_width = self.config['caption_width']
        border_padding = self.config['border_padding']
        text_width = self.caption_width - (border_padding * 2)

        # create a text-only image without border padding
        font_size = self.config['font_size']
        fg_r = 255 * self.config['fg_r']
        fg_g = 255 * self.config['fg_r']
        fg_b = 255 * self.config['fg_r']
        fg_a = self.config['fg_a'] / 100
        text_img = os.path.join(self.conf_dir, 'text.png')

        cmd = \
            f'convert \
            -size {text_width} \
            -pointsize {font_size} \
            -background none \
            -fill rgba({fg_r},{fg_g},{fg_b},{fg_a}) \
            caption:\"{self.str_caption}\" \
            {text_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # get height of text-only image
        cmd = \
            f'identify \
            -format \
            %[fx:h] \
            {text_img}'
        cmd_array = shlex.split(cmd)
        res = subprocess.check_output(cmd_array)
        text_height = int(res.decode('UTF-8'))

        if DEBUG:
            print('text_width:', text_width)
            print('text_height:', text_height)

        # create background image
        self.caption_height = text_height + (border_padding * 2)
        bg_r = 255 * self.config['bg_r']
        bg_g = 255 * self.config['bg_r']
        bg_b = 255 * self.config['bg_r']
        bg_a = self.config['bg_a'] / 100
        corner_radius = self.config['corner_radius']
        back_img = os.path.join(self.conf_dir, 'back.png')

        cmd = \
            f'convert \
            -size {self.caption_width}x{self.caption_height} \
            xc:none \
            -fill \"rgba({bg_r},{bg_g},{bg_b},{bg_a})\" \
            -draw \
            \"roundRectangle \
            0,\
            0,\
            {self.caption_width},\
            {self.caption_height}, \
            {corner_radius},\
            {corner_radius}\" \
            {back_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # create a file path for caption image
        self.capt_img = os.path.join(self.conf_dir, 'capt.png')

        if DEBUG:
            print('capt_img:', self.capt_img)

        # combine text and back images
        cmd = f'convert \
            {back_img} \
            {text_img} \
            -gravity center \
            -compose over \
            -composite \
            {self.capt_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with temp images
        os.system(f'rm {text_img}')
        os.system(f'rm {back_img}')

        # log success
        logging.debug('create caption image')

    # --------------------------------------------------------------------------
    # Combine original image and caption
    # --------------------------------------------------------------------------
    def __combine_images(self):

        # TODO: move this to its own function and error check
        with open(self.capt_file, 'r') as file:
            self.capt_data = json.load(file)

        # get the path to the image
        pic_path = self.capt_data['filepath']

        if DEBUG:
            print('pic_path:', pic_path)

        # get the position of the caption
        x_pos, y_pos = self.__get_position()

        if DEBUG:
            print('x_pos:', x_pos)
            print('y_pos:', y_pos)

        # make the final image
        cmd = f'convert \
            {pic_path} \
            {self.capt_img} \
            -geometry +{x_pos}+{y_pos} \
            -compose over \
            -composite \
            {pic_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with mask
        os.system(f'rm {self.capt_img}')

        logging.debug('combine images')

    # --------------------------------------------------------------------------
    # Get x and y position of caption
    # --------------------------------------------------------------------------
    def __get_position(self):

        # # TODO: remove pic/screen size after getting info from file
        # # get size of pic
        # cmd = \
        #     f'identify \
        #     -format \
        #     %[fx:w] \
        #     {self.pic_path}'
        # cmd_array = shlex.split(cmd)
        # res = subprocess.check_output(cmd_array)
        # pic_width = int(res.decode('UTF-8'))

        # cmd = \
        #     f'identify \
        #     -format \
        #     %[fx:h] \
        #     {self.pic_path}'
        # cmd_array = shlex.split(cmd)
        # res = subprocess.check_output(cmd_array)
        # pic_height = int(res.decode('UTF-8'))

        # # get size of screen
        # display = Gdk.Display.get_default()
        # monitor = display.get_primary_monitor()
        # geometry = monitor.get_geometry()
        # screen_width = geometry.width
        # screen_height = geometry.height

        pic_width = self.capt_data['pic_w']
        pic_height = self.capt_data['pic_h']
        screen_width = self.capt_data['screen_w']
        screen_height = self.capt_data['screen_h']

        # get the overhang of the image (amount of picture not on screen)
        x_overhang = (pic_width - screen_width) / 2
        y_overhang = (pic_height - screen_height) / 2

        side_padding = self.config['side_padding']
        top_padding = self.config['top_padding']
        bottom_padding = self.config['bottom_padding']

        # default position is bottom right
        x_pos = pic_width - x_overhang - self.caption_width - side_padding
        y_pos = pic_height - y_overhang - self.caption_height - bottom_padding

        position = self.config['position']
        if position == 0:
            x_pos = x_overhang + side_padding
            y_pos = y_overhang + top_padding
        elif position == 1:
            x_pos = x_overhang + (screen_width / 2) - (self.caption_width / 2)
            y_pos = y_overhang + top_padding
        elif position == 2:
            x_pos = pic_width - x_overhang - self.caption_width - side_padding
            y_pos = y_overhang + top_padding
        elif position == 3:
            x_pos = x_overhang + side_padding
            y_pos = y_overhang + (screen_height / 2) - (self.caption_height / 2)
        elif position == 4:
            x_pos = x_overhang + (screen_width / 2) - (self.caption_width / 2)
            y_pos = y_overhang + (screen_height / 2) - (self.caption_height / 2)
        elif position == 5:
            x_pos = x_overhang - screen_width - self.caption_width - side_padding
            y_pos = y_overhang + (screen_height / 2) - (self.caption_height / 2)
        elif position == 6:
            x_pos = x_overhang + side_padding
            y_pos = pic_height - y_overhang - self.caption_height - bottom_padding
        elif position == 7:
            x_pos = x_overhang + (screen_width / 2) - (self.caption_width / 2)
            y_pos = y_overhang - screen_height - self.caption_height - bottom_padding
        elif position == 8:
            x_pos = pic_width - x_overhang - self.caption_width - side_padding
            y_pos = pic_height - y_overhang - self.caption_height - bottom_padding

        # round off values if division goes wonky
        x_pos = int(x_pos)
        y_pos = int(y_pos)

        return x_pos, y_pos


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    caption = Caption()
    caption.run()

# -)

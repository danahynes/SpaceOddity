#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_c.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: check for title/copyright/expl and any other data in apod_data
# also better formatting if one or more not preset
# TODO: redirect all imagemagick errors to log file
# TODO: fix alpha for foreground/background
# TODO: convert imagemagick calls to wand
# TODO: limit on cqption is ~1000 cahracters
# TODO: put mask/background/text into one operation?
# maybe convert original to png?
# TODO: remove DEBUG

# NB: requires :
# imagemagick (sudo apt install imagemagick)
# wand (pip install wand)
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
import tkinter

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

        self.prog_name = 'spaceoddity'

        # get locations
        home_dir = os.path.expanduser('~')
        self.conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.data_file = os.path.join(self.conf_dir, f'{self.prog_name}.dat')
        log_file = os.path.join(self.conf_dir, f'{self.prog_name}.log')
        self.conf_file = os.path.join(self.conf_dir, f'{self.prog_name}.json')

        if DEBUG:
            print('home_dir:', home_dir)
            print('conf_dir:', self.conf_dir)
            print('data_file:', self.data_file)
            print('log_file:', log_file)
            print('conf_file:', self.conf_file)

        # set up logging
        logging.basicConfig(filename=log_file, filemode='a',
                            level=logging.DEBUG,
                            format='%(asctime)s - %(message)s')

        # log start
        logging.debug('-----------------------------------------------------------')
        logging.debug('Start caption script')

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

            if DEBUG:
                print('caption disabled')

            # log that we are finished with script
            self.__exit('caption disabled', 0)

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):
        self.__get_data()
        self.__resize_image()
        self.__make_caption()
        self.__combine_images()

        if DEBUG:
            print('all done')

        # exit gracefully
        self.__exit('all done', 0)

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def __exit(self, msg, code):

        # log that we are finished with script
        logging.debug('%s, exit caption script', msg)
        logging.debug('-------------------------------------------------------')

        # quit script
        # NB: VSCode doesn't like using exit with any other code than 0
        # exit(code)
        exit(0)

    # --------------------------------------------------------------------------
    # Loads the config dict from a file
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
                logging.debug('load config file: %s', self.conf_file)
            except json.JSONDecodeError as err:
                self.config = dict(self.config_defaults)
                logging.debug('error: %s', err.reason)
                logging.debug('could not load json, loading defaults')
                self.__save_config()

                if DEBUG:
                    print('could not load json, loading defaults:', err.reason)

        # get values or defaults
        for key in self.config_defaults:
            if key not in self.config.keys():
                self.config[key] = self.config_defaults.get(key)

        if DEBUG:
            print('load config:', self.config)

    # --------------------------------------------------------------------------
    # Saves the user config dict to a file
    # --------------------------------------------------------------------------
    def __save_config(self):

        # open the file and write json
        with open(self.conf_file, 'w') as file:
            json.dump(self.config, file, indent=4)

        logging.debug('save config file: %s', self.conf_file)

        if DEBUG:
            print('save config:', self.config)

    # --------------------------------------------------------------------------
    # Get data file (the apod data downloaded by main script)
    # --------------------------------------------------------------------------
    def __get_data(self):

        # open data file
        with open(self.data_file, 'r') as file:
            apod_data = json.load(file)

        # get the url to the actual image
        if 'hdurl' in apod_data.keys():
            pic_url = apod_data['hdurl']
        elif 'url' in apod_data.keys():
            pic_url = apod_data['url']

        # create a download file path
        file_ext = pic_url.split('.')[-1]
        pic_name = f'{self.prog_name}_desk.{file_ext}'
        self.pic_path = os.path.join(self.conf_dir, pic_name)

        if DEBUG:
            print('pic_url:', pic_url)
            print('file_ext:', file_ext)
            print('pic_name:', pic_name)
            print('pic_path:', self.pic_path)

        # get data for caption
        self.str_title = ''
        if 'title' in apod_data.keys():
            self.str_title = apod_data['title']
        self.str_copyright = ''
        if 'copyright' in apod_data.keys():
            self.str_copyright = apod_data['copyright']
        self.str_text = ''
        if 'explanation' in apod_data.keys():
            self.str_text = apod_data['explanation']

        logging.debug('got data from json file')

        if DEBUG:
            print('str_title:', self.str_title)
            print('str_copyright:', self.str_copyright)
            print('str_text:', self.str_text)

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
        pic_w = int(res.decode('UTF-8'))

        cmd = \
            f'identify \
            -format \
            %[fx:h] \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        res = subprocess.check_output(cmd_array)
        pic_h = int(res.decode('UTF-8'))

        if DEBUG:
            print('pic_w:', pic_w)
            print('pic_h:', pic_h)

        # get screen size
        root = tkinter.Tk()
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        if DEBUG:
            print('screen_w:', self.screen_w)
            print('screen_h:', self.screen_h)

        # get the scale factor for height and width
        scale_w = pic_w / self.screen_w
        scale_h = pic_h / self.screen_h

        if DEBUG:
            print('scale_w:', scale_w)
            print('scale_h:', scale_h)

        # use the smallest scale to get the biggest new dimension
        scale = scale_w if scale_w < scale_h else scale_h

        # get the scaled height/width and make sure it still fills the screen
        # after rounding with an int cast
        tmp_w = int(pic_w / scale)
        self.new_w = self.screen_w if tmp_w < self.screen_w else tmp_w
        tmp_h = int(pic_h / scale)
        self.new_h = self.screen_h if tmp_h < self.screen_h else tmp_h

        if DEBUG:
            print('new_w:', self.new_w)
            print('new_h:', self.new_h)

        # do the resize
        cmd = \
            f'convert \
            {self.pic_path} \
            -resize {self.new_w}x{self.new_h} \
            -extent {self.new_w}x{self.new_h} \
            -gravity center \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        logging.debug('resized image')

    # --------------------------------------------------------------------------
    # Make caption png
    # --------------------------------------------------------------------------
    def __make_caption(self):

        # create some file names
        self.capt_img = os.path.join(self.conf_dir, f'{self.prog_name}_capt.png')

        if DEBUG:
            print('capt_img:', self.capt_img)

        # form a string from shown attributes
        str_caption = ''
        if self.config['show_title'] and self.str_title != '':
            str_caption = str_caption + self.str_title + '\n\n'
        if self.config['show_copyright'] and self.str_copyright != '':
            str_caption = str_caption + self.str_copyright + '\n\n'
        if self.config['show_text'] and self.str_text != '':
            str_caption = str_caption + self.str_text

        # NB: limit on cqption is ~1000 cahracters
        len_caption = len(str_caption)

        if DEBUG:
            print('len_caption:', len_caption)

        str_caption = str_caption[0:1000]

        if DEBUG:
            print('str_caption:', str_caption)

        # remove border size for text-only png
        self.cap_w = self.config['caption_width']
        border_padding = self.config['border_padding']
        tmp_w = self.cap_w - (border_padding * 2)

        # create a text-only image for sizing
        text_img = os.path.join(self.conf_dir, 'text.png')
        font_size = self.config['font_size']
        tmp_r = 255 * self.config['fg_r']
        tmp_g = 255 * self.config['fg_r']
        tmp_b = 255 * self.config['fg_r']
        tmp_a = self.config['fg_a'] / 100
        cmd = \
            f'convert \
            -size {tmp_w} \
            -pointsize {font_size} \
            -background none \
            -fill rgba({tmp_r},{tmp_g},{tmp_b},{tmp_a}) \
            caption:\"{str_caption}\" \
            {text_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # get size of text
        cmd = \
            f'identify \
            -format \
            %[fx:w] \
            {text_img}'
        cmd_array = shlex.split(cmd)
        res = subprocess.check_output(cmd_array)
        text_w = int(res.decode('UTF-8'))

        cmd = \
            f'identify \
            -format \
            %[fx:h] \
            {text_img}'
        cmd_array = shlex.split(cmd)
        res = subprocess.check_output(cmd_array)
        text_h = int(res.decode('UTF-8'))

        if DEBUG:
            print('text_w:', text_w)
            print('text_h:', text_h)

        # create background image with text
        # back_img = os.path.join(self.conf_dir, 'back.png')
        self.cap_h = text_h + (border_padding * 2)
        tmp_r = 255 * self.config['bg_r']
        tmp_g = 255 * self.config['bg_r']
        tmp_b = 255 * self.config['bg_r']
        tmp_a = self.config['bg_a'] / 100
        cmd = \
            f'convert \
            -size {self.cap_w}x{self.cap_h} \
            xc:\"rgba({tmp_r},{tmp_g},{tmp_b},{tmp_a})\" \
            -gravity center \
            {text_img} \
            -composite \
            {self.capt_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with text-only image
        os.system(f'rm {text_img}')

        # create mask
        mask_img = os.path.join(self.conf_dir, 'mask.png')
        corner_radius = self.config['corner_radius']
        cmd = \
            f'convert \
            -size {self.cap_w}x{self.cap_h} \
            xc:none \
            -draw \
            \"roundRectangle \
            0,\
            0,\
            {self.cap_w},\
            {self.cap_h}, \
            {corner_radius},\
            {corner_radius}\" \
            {mask_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # apply mask to text image
        cmd = \
            f'convert \
            {self.capt_img} \
            -matte {mask_img} \
            -compose DstIn \
            -composite \
            {self.capt_img}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with mask
        os.system(f'rm {mask_img}')

        logging.debug('Created text image')

    # --------------------------------------------------------------------------
    # Combine original image and caption
    # --------------------------------------------------------------------------
    def __combine_images(self):

        # get the overhang of the image (amount of picture not on screen)
        x_over = (self.new_w - self.screen_w) / 2
        y_over = (self.new_h - self.screen_h) / 2

        if DEBUG:
            print('x_over:', x_over)
            print('y_over:', y_over)

        position = self.config['position']
        side_padding = self.config['side_padding']
        top_padding = self.config['top_padding']
        bottom_padding = self.config['bottom_padding']

        # default position is bottom right
        x_pos = self.new_w - x_over - self.cap_w - side_padding
        y_pos = self.new_h - y_over - self.cap_h - bottom_padding

        if position == 0:
            x_pos = x_over + side_padding
            y_pos = y_over + top_padding
        elif position == 1:
            x_pos = x_over + (self.screen_w / 2) - (self.cap_w / 2)
            y_pos = y_over + top_padding
        elif position == 2:
            x_pos = self.new_w - x_over - self.cap_w - side_padding
            y_pos = y_over + top_padding
        elif position == 3:
            x_pos = x_over + side_padding
            y_pos = y_over + (self.screen_h / 2) - (self.cap_h / 2)
        elif position == 4:
            x_pos = x_over + (self.screen_w / 2) - (self.cap_w / 2)
            y_pos = y_over + (self.screen_h / 2) - (self.cap_h / 2)
        elif position == 5:
            x_pos = x_over - self.screen_w - self.cap_w - side_padding
            y_pos = y_over + (self.screen_h / 2) - (self.cap_h / 2)
        elif position == 6:
            x_pos = x_over + side_padding
            y_pos = self.new_h - y_over - self.cap_h - bottom_padding
        elif position == 7:
            x_pos = x_over + (self.screen_w / 2) - (self.cap_w / 2)
            y_pos = y_over - self.screen_h - self.cap_h - bottom_padding
        elif position == 8:
            x_pos = self.new_w - x_over - self.cap_w - side_padding
            y_pos = self.new_h - y_over - self.cap_h - bottom_padding

        # round off values if division goes wonky
        x_pos = int(x_pos)
        y_pos = int(y_pos)

        if DEBUG:
            print('position:', position)
            print('x_pos:', x_pos)
            print('y_pos:', y_pos)

        # make the final image
        cmd = f'convert \
            {self.pic_path} \
            {self.capt_img} \
            -geometry +{x_pos}+{y_pos} \
            -compose over \
            -composite \
            {self.pic_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with mask
        os.system(f'rm {self.capt_img}')

        logging.debug('combined images')


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    caption = Caption()
    caption.run()

# -)

#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_caption.py                               /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: test all options

# FIXME: caption length must be relative to font size (size limit on image)
#   at 12 points, limit as about 1000
#   this may have to do with giving the convert only one dimension so it
#   assumes a square image - how to fix this?

# TODO: some imagemagick python binding (wand?)

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import json
import logging
import os
import shlex
import subprocess

# NB: requires:
# imagemagick (apt)

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
        prog_name = 'spaceoddity'

        # get locations
        home_dir = os.path.expanduser('~')
        self.conf_dir = os.path.join(home_dir, '.config', prog_name)
        self.conf_path = os.path.join(self.conf_dir, f'{prog_name}.cfg')
        log_path = os.path.join(self.conf_dir, f'{prog_name}.log')

        # user config dict
        self.conf_dict = {}

        # set up logging
        logging.basicConfig(filename=log_path, level=logging.DEBUG,
                            format='%(asctime)s %(levelname)-7s %(message)s',
                            datefmt='%Y-%m-%d %I:%M:%S %p')

        # log start
        logging.debug('-------------------------------------------------------')
        logging.debug('start caption script')

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # init the config dict from user settings
        self.__load_conf()

        # check to see if we are enabled
        options = self.conf_dict['options']
        if options['show_caption']:

            # call each step in the process
            self.make_caption()
            self.combine_images()

        else:

            # log the enabled state
            logging.debug('caption script disabled')

        # exit gracefully
        self.do_exit()

    # -------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Make caption png
    # --------------------------------------------------------------------------
    def make_caption(self):

        # get options
        options = self.conf_dict['options']

        # remove border size for text-only png
        capt_width = options['width']
        border_padding = options['border_padding']
        text_width = capt_width - (border_padding * 2)

        # get text options
        font_size = options['font_size']
        font_r = options['font_r'] * 255
        font_g = options['font_g'] * 255
        font_b = options['font_b'] * 255

        # get the text to draw
        str_caption = self.__get_text()

        # create a path to save to
        text_path = os.path.join(self.conf_dir, 'text.png')

        cmd = \
            f'convert \
            -size {text_width} \
            -pointsize {font_size} \
            -background none \
            -fill rgba({font_r},{font_g},{font_b},1.0) \
            caption:\"{str_caption}\" \
            {text_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # get text height
        cmd = \
            f'identify \
            -format %h \
            {text_path}'
        cmd_array = shlex.split(cmd)
        out = subprocess.check_output(cmd_array)
        text_height = int(out)

        # add the border into the height
        capt_height = text_height + (border_padding * 2)

        # save caption height for placement
        capt_dict = self.conf_dict['caption']
        capt_dict['height'] = capt_height

        # get background options
        bg_r = options['bg_r'] * 255
        bg_g = options['bg_g'] * 255
        bg_b = options['bg_b'] * 255
        bg_a = options['bg_a'] / 100
        corner_radius = options['corner_radius']

        # create a path to the background image
        back_path = os.path.join(self.conf_dir, 'back.png')

        # create background image
        cmd = \
            f'convert \
            -size {capt_width}x{capt_height} \
            xc:none \
            -fill \"rgba({bg_r},{bg_g},{bg_b},{bg_a})\" \
            -draw \
            \"roundRectangle \
            0,\
            0,\
            {capt_width},\
            {capt_height}, \
            {corner_radius},\
            {corner_radius}\" \
            {back_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # create a file path for caption image
        capt_path = os.path.join(self.conf_dir, 'capt.png')

        # combine text and back images
        cmd = f'convert \
            {back_path} \
            {text_path} \
            -gravity center \
            -compose over \
            -composite \
            {capt_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with temp images
        os.remove(text_path)
        os.remove(back_path)

        # log success
        logging.debug('make caption')

    # --------------------------------------------------------------------------
    # Combine original image and caption
    # --------------------------------------------------------------------------
    def combine_images(self):

        # get the user options
        files_dict = self.conf_dict['files']

        # get the path to the image
        pic_path = files_dict['filepath']

        # get the position of the caption
        x_pos, y_pos = self.__get_position()

        # create a file path for caption image
        capt_path = os.path.join(self.conf_dir, 'capt.png')

        # make the final image
        cmd = f'convert \
            {pic_path} \
            {capt_path} \
            -geometry +{x_pos}+{y_pos} \
            -compose over \
            -composite \
            {pic_path}'
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        # done with caption
        os.remove(capt_path)

        # log success
        logging.debug('combine images')

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def do_exit(self):

        # save config dict to file
        self.__save_conf()

        # log that we are finished with script
        logging.debug('exit caption script')
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

        # read config file
        with open(self.conf_path, 'r') as file:
            try:
                self.conf_dict = json.load(file)

                # log success
                logging.debug('load conf file: %s', self.conf_dict)

            except json.JSONDecodeError as error:

                # log error
                logging.error(error)
                logging.error('could not load config file')

                # this is a fatal error
                self.do_exit()

    # --------------------------------------------------------------------------
    # Save dictionary data to a file
    # --------------------------------------------------------------------------
    def __save_conf(self):

        # open the file and write json
        with open(self.conf_path, 'w') as file:
            json.dump(self.conf_dict, file, indent=4)

        # log success
        logging.debug('save conf file: %s', self.conf_dict)

    # --------------------------------------------------------------------------
    # Get the text to show in the caption bubble
    # --------------------------------------------------------------------------
    def __get_text(self):

        # get user options
        options = self.conf_dict['options']
        show_title = options['show_title']
        show_copyright = options['show_copyright']
        show_explanation = options['show_explanation']

        # get apod options
        apod_data = self.conf_dict['apod']
        has_title = apod_data['title']
        has_copyright = apod_data['copyright']
        has_explanation = apod_data['explanation']

        # find out which attributes to show
        show_has_title = ''
        show_has_copyright = ''
        show_has_explanation = ''
        if show_title and has_title != '':
            show_has_title = has_title
        if show_copyright and has_copyright != '':
            show_has_copyright = has_copyright
        if show_explanation and has_explanation != '':
            show_has_explanation = has_explanation

        # move to subroutine to avoid complexity
        str_caption = self.__format_caption(show_has_title, show_has_copyright,
                                            show_has_explanation)

        # log success
        logging.debug('get caption: %s', str_caption)

        # return the final string
        return str_caption

    # --------------------------------------------------------------------------
    # Formats the displayed caption based on what attributes are shown
    # --------------------------------------------------------------------------
    def __format_caption(self, show_has_title, show_has_copyright,
                         show_has_explanation):

        # format string based on shown attributes
        str_caption = ''
        if not show_has_title and not show_has_copyright \
                and not show_has_explanation:
            str_caption = ''
        elif not show_has_title and not show_has_copyright \
                and show_has_explanation:
            str_caption = show_has_explanation
        elif not show_has_title and show_has_copyright \
                and not show_has_explanation:
            str_caption = show_has_copyright
        elif not show_has_title and show_has_copyright \
                and show_has_explanation:
            str_caption = show_has_copyright + '\n\n' + show_has_explanation
        elif show_has_title and not show_has_copyright \
                and not show_has_explanation:
            str_caption = show_has_title
        elif show_has_title and not show_has_copyright and show_has_explanation:
            str_caption = show_has_title + '\n\n' + show_has_explanation
        elif show_has_title and show_has_copyright and not show_has_explanation:
            str_caption = show_has_title + '\n\n' + show_has_copyright
        elif show_has_title and show_has_copyright and show_has_explanation:
            str_caption = show_has_title + '\n\n' + show_has_copyright + \
                '\n\n' + show_has_explanation

        str_caption = str_caption[:1000]

        # log success
        logging.debug('format caption: %s', str_caption)

        # return the final string
        return str_caption

    # --------------------------------------------------------------------------
    # Get x and y position of caption
    # --------------------------------------------------------------------------
    def __get_position(self):

        # get user options
        options = self.conf_dict['options']
        width = options['width']
        side_padding = options['side_padding']
        top_padding = options['top_padding']
        bottom_padding = options['bottom_padding']

        # get settings from user dict
        caption = self.conf_dict['caption']
        height = caption['height']
        pic_width = caption['pic_w']
        pic_height = caption['pic_h']
        screen_width = caption['screen_w']
        screen_height = caption['screen_h']

        # get the overhang of the image (amount of picture not on screen)
        x_overhang = (pic_width - screen_width) / 2
        y_overhang = (pic_height - screen_height) / 2

        # default position is bottom right (8)
        x_pos = pic_width - x_overhang - width - side_padding
        y_pos = pic_height - y_overhang - height - bottom_padding

        # get x, y from position
        position = options['position']
        if position == 0:
            x_pos = x_overhang + side_padding
            y_pos = y_overhang + top_padding
        elif position == 1:
            x_pos = x_overhang + (screen_width / 2) - (width / 2)
            y_pos = y_overhang + top_padding
        elif position == 2:
            x_pos = pic_width - x_overhang - width - side_padding
            y_pos = y_overhang + top_padding
        elif position == 3:
            x_pos = x_overhang + side_padding
            y_pos = y_overhang + (screen_height / 2) - (height / 2)
        elif position == 4:
            x_pos = x_overhang + (screen_width / 2) - (width / 2)
            y_pos = y_overhang + (screen_height / 2) - (height / 2)
        elif position == 5:
            x_pos = x_overhang - screen_width - width - \
                side_padding
            y_pos = y_overhang + (screen_height / 2) - (height / 2)
        elif position == 6:
            x_pos = x_overhang + side_padding
            y_pos = pic_height - y_overhang - height - \
                bottom_padding
        elif position == 7:
            x_pos = x_overhang + (screen_width / 2) - (width / 2)
            y_pos = y_overhang - screen_height - height - \
                bottom_padding
        elif position == 8:
            x_pos = pic_width - x_overhang - width - side_padding
            y_pos = pic_height - y_overhang - height - \
                bottom_padding

        # round off values if division goes wonky
        x_pos = int(x_pos)
        y_pos = int(y_pos)

        logging.debug('get position: %i, %s', x_pos, y_pos)

        # return result as tuple
        return x_pos, y_pos


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    caption = Caption()
    caption.run()

# -)

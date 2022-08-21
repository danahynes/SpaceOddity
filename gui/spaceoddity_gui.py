#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_gui.py                                   /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 08/02/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: doesn't delete old image when apply after loading defaults
# TODO: also doesn't set picture-uri-dark in dconf (works from main)
# TODO: get_font_name/set_font_name is depercated
# TODO: just use font size for now
# TODO: parse font using PangoFontDescription
# TODO: check all options
# TODO: use gtkapplication
# TODO: grouping of controls - see settings (deep dark box),
# login manager (light box w/separator) look at some settings glade files
# TODO: i18n glade file objects with comments
# TODO: tooltips (and i18n *them* with comments)
# TODO: config keys as constants
# TODO: config defaults in shared module
# TODO: object names as constants
# TODO: remove DEBUG


# NB: requires:
# pygobject

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import gettext
import json
import locale
import logging
import os
import shlex
import subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa: E402 (ignore import order)

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class Gui:

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
        self.app_dir = os.path.join(home_dir, f'.{self.prog_name}')
        conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.conf_path = os.path.join(conf_dir, f'{self.prog_name}.cfg')
        gui_path = os.path.join(self.app_dir, 'gui', f'{self.prog_name}.glade')
        loc_dir = os.path.join(self.app_dir, 'gui', 'locale')
        log_path = os.path.join(conf_dir, f'{self.prog_name}.log')

        # create folder if it does not exist
        if not os.path.exists(conf_dir):
            os.mkdir(conf_dir)

        # set up logging
        logging.basicConfig(filename=log_path, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # log start
        logging.debug('-------------------------------------------------------')
        logging.debug('start gui script')

        # set default config dict
        self.conf_dict_def = {
            'options': {
                'enabled':          1,
                'show_caption':     1,
                'show_title':       1,
                'show_copyright':   1,
                'show_explanation': 1,
                'show_date':        1,
                'font':             'Sans Regular 10',
                'font_r':           1.0,
                'font_g':           1.0,
                'font_b':           1.0,
                'bg_r':             0.0,
                'bg_g':             0.0,
                'bg_b':             0.0,
                'bg_a':             75,
                'position':         8,
                'width':            500,
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
        self.conf_dict = self.conf_dict_def.copy()

        # set up locale
        locale.setlocale(locale.LC_ALL, '')
        locale.bindtextdomain(self.prog_name, loc_dir)

        # set up gettext
        gettext.bindtextdomain(self.prog_name, loc_dir)
        gettext.textdomain(self.prog_name)

        # set up builder and load gui file
        builder = Gtk.Builder()
        builder.set_translation_domain(self.prog_name)
        builder.add_from_file(gui_path)
        builder.connect_signals(self)

        # get objects in gui
        self.win_main = builder.get_object('win_main')

        # general page
        self.switch_enabled = builder.get_object('switch_enabled')
        self.switch_show_caption = builder.get_object('switch_show_caption')
        self.switch_show_title = builder.get_object('switch_show_title')
        self.switch_show_copyright = builder.get_object('switch_show_copyright')
        self.switch_show_explanation = builder.get_object(
            'switch_show_explanation')

        # font and colors page
        self.btn_font = builder.get_object('btn_font')
        self.btn_font_color = builder.get_object('btn_font_color')
        self.btn_bg_color = builder.get_object('btn_bg_color')
        self.scale_bg_transparency = builder.get_object(
            'scale_bg_transparency')

        # layout page
        self.combo_position = builder.get_object('combo_position')
        self.scale_width = builder.get_object('scale_width')
        self.scale_corner_radius = builder.get_object('scale_corner_radius')
        self.scale_border_padding = builder.get_object('scale_border_padding')
        self.scale_top_padding = builder.get_object('scale_top_padding')
        self.scale_bottom_padding = builder.get_object('scale_bottom_padding')
        self.scale_side_padding = builder.get_object('scale_side_padding')

        # about dialog
        self.dlg_about = builder.get_object('dlg_about')

        # set version in about dialog
        # TODO: make this the final location of the version file
        vers_path = os.path.join(self.app_dir, '../static/VERSION.txt')
        with open(vers_path, 'r') as file:
            version = file.readline()
        self.dlg_about.set_version(version)

    # --------------------------------------------------------------------------
    # Run the gui
    # --------------------------------------------------------------------------
    def run(self):

        # init the config dict from user settings
        self.__load_conf()

        # call each step in the process
        self.__load_gui(self.conf_dict)

        # run gtk main loop
        self.win_main.show_all()
        Gtk.main()

        # exit gracefully
        self.__exit()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Load the gui state from the specified dict (user or default)
    # --------------------------------------------------------------------------
    def __load_gui(self, dictionary):

        # get options from dictionary
        options = dictionary['options']

        # set up general page
        self.switch_enabled.set_active(options['enabled'])
        self.switch_show_caption.set_active(options['show_caption'])
        self.switch_show_title.set_active(options['show_title'])
        self.switch_show_copyright.set_active(options['show_copyright'])
        self.switch_show_explanation.set_active(options['show_explanation'])

        # set up font & colors page
        font = options['font']
        self.btn_font.set_font_name(font)
        color = Gdk.RGBA()
        color.red = options['font_r']
        color.green = options['font_g']
        color.blue = options['font_b']
        self.btn_font_color.set_rgba(color)
        color = Gdk.RGBA()
        color.red = options['bg_r']
        color.green = options['bg_g']
        color.blue = options['bg_b']
        self.btn_bg_color.set_rgba(color)
        self.__set_adj_value(self.scale_bg_transparency, options['bg_a'])

        self.combo_position.set_active(options['position'])
        self.__set_adj_value(self.scale_width, options['width'])
        self.__set_adj_value(self.scale_corner_radius, options['corner_radius'])
        self.__set_adj_value(self.scale_border_padding,
                             options['border_padding'])
        self.__set_adj_value(self.scale_top_padding, options['top_padding'])
        self.__set_adj_value(self.scale_bottom_padding,
                             options['bottom_padding'])
        self.__set_adj_value(self.scale_side_padding, options['side_padding'])

        logging.debug('load gui: %s', dictionary)

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def __exit(self):

        # log that we are finished with script
        logging.debug('exit gui script')
        logging.debug('-------------------------------------------------------')

        # quit script
        exit()

    # --------------------------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Callback for when the window is closed
    # --------------------------------------------------------------------------
    def win_main_destroy(self, *args):

        # stop the loop and exit script
        Gtk.main_quit()

        # exit gracefully
        self.__exit()

    # --------------------------------------------------------------------------
    # Callback for when the 'Apply' button is clicked
    # --------------------------------------------------------------------------
    def btn_apply_clicked(self, *args):

        # save gui to dict
        self.__save_gui()

        # save dict to file
        self.__save_conf()

        # rerun main script now
        scpt_path = os.path.join(self.app_dir, f'{self.prog_name}_main.py')

        # set cmd for running caption
        cmd = scpt_path
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        logging.debug('btn_apply_clicked')

    # --------------------------------------------------------------------------
    # Callback for when 'Reload user settings' menu item is clicked
    # --------------------------------------------------------------------------
    def menu_item_user_clicked(self, *args):

        # load user settings and apply to gui
        self.__load_conf()
        self.__load_gui(self.conf_dict)

        logging.debug('menu_item_user_clicked')

    # --------------------------------------------------------------------------
    # Callback for when the 'Load defaults' menu item is clicked
    # --------------------------------------------------------------------------
    def menu_item_defaults_clicked(self, *args):

        # load default settings and apply to gui
        self.__load_gui(self.conf_dict_def)

        logging.debug('menu_item_defaults_clicked')

    # --------------------------------------------------------------------------
    # Callback for when the 'About' menu item is clicked
    # --------------------------------------------------------------------------
    def menu_item_about_clicked(self, *args):

        # run the dailog modally, then hide (not destroy!)
        self.dlg_about.run()
        self.dlg_about.hide()

        logging.debug('menu_item_about_clicked')

    # --------------------------------------------------------------------------
    # Callback for when the 'Enabled' switch is toggled
    # --------------------------------------------------------------------------
    def switch_enabled_set_state(self, *args):

        # enable/disable controls based on setting
        self.__check_enable()

        logging.debug('switch_enabled_set_state')

    # --------------------------------------------------------------------------
    # Callback for when the 'Caption' switch is toggled
    # --------------------------------------------------------------------------
    def switch_show_caption_set_state(self, *args):

        # enable/disable controls based on setting
        self.__check_enable()

        logging.debug('switch_show_caption_set_state')

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Save the gui state to the user dict
    # --------------------------------------------------------------------------
    def __save_gui(self):

        # get user dictionary
        options = self.conf_dict['options']

        # save general page
        options['enabled'] = self.switch_enabled.get_active()
        options['show_caption'] = self.switch_show_caption.get_active()
        options['show_title'] = self.switch_show_title.get_active()
        options['show_copyright'] = self.switch_show_copyright.get_active()
        options['show_explanation'] = self.switch_show_explanation.get_active()

        # save font & colors page
        font = self.btn_font.get_font_name()
        options['font'] = font
        color = self.btn_font_color.get_rgba()
        options['font_r'] = color.red
        options['font_g'] = color.green
        options['font_b'] = color.blue
        color = self.btn_bg_color.get_rgba()
        options['bg_r'] = color.red
        options['bg_g'] = color.green
        options['bg_b'] = color.blue
        options['bg_a'] = self.__get_adj_value(self.scale_bg_transparency)

        # save layout page
        options['position'] = self.combo_position.get_active()
        options['width'] = self.__get_adj_value(self.scale_width)
        options['corner_radius'] = self.__get_adj_value(
            self.scale_corner_radius)
        options['border_padding'] = self.__get_adj_value(
            self.scale_border_padding)
        options['top_padding'] = self.__get_adj_value(self.scale_top_padding)
        options['bottom_padding'] = self.__get_adj_value(
            self.scale_bottom_padding)
        options['side_padding'] = self.__get_adj_value(
            self.scale_side_padding)

        logging.debug('save_gui: %s', self.conf_dict)

    # --------------------------------------------------------------------------
    # Get the adjustment value of the specified object
    # --------------------------------------------------------------------------
    def __get_adj_value(self, obj):

        # function to shorten function call
        return obj.get_adjustment().get_value()

        logging.debug('get_adj_value')

    # --------------------------------------------------------------------------
    # Set the adjustment value of the specified object
    # --------------------------------------------------------------------------
    def __set_adj_value(self, obj, value):

        # function to shorten function call
        obj.get_adjustment().set_value(value)

        logging.debug('set_adj_value')

    # --------------------------------------------------------------------------
    # Load dictionary data from a file
    # --------------------------------------------------------------------------
    def __load_conf(self):

        # make sure conf file exists
        if not os.path.exists(self.conf_path):
            self.conf_dict = self.conf_dict_def.copy()
            self.__save_conf()

        # open the file and read json
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
    # Saves the user config dict to a file
    # --------------------------------------------------------------------------
    def __save_conf(self):

        # open the file and write json
        with open(self.conf_path, 'w') as file:
            json.dump(self.conf_dict, file, indent=4)

        logging.debug('save config file: %s', self.conf_path)

    # --------------------------------------------------------------------------
    # Enables or disables controls based on the state of the first two switches
    # --------------------------------------------------------------------------
    def __check_enable(self):

        # check enabled state of all controls
        enabled = self.switch_enabled.get_active()
        show_caption = self.switch_show_caption.get_active()

        # enable/disable all controls based on above state
        self.switch_show_caption.set_sensitive(enabled)
        self.switch_show_title.set_sensitive(enabled and show_caption)
        self.switch_show_copyright.set_sensitive(enabled and show_caption)
        self.switch_show_explanation.set_sensitive(enabled and show_caption)
        self.btn_font_color.set_sensitive(enabled and show_caption)
        self.btn_bg_color.set_sensitive(enabled and show_caption)
        self.scale_bg_transparency.set_sensitive(enabled and show_caption)
        self.combo_position.set_sensitive(enabled and show_caption)
        self.scale_width.set_sensitive(enabled and show_caption)
        self.scale_corner_radius.set_sensitive(enabled) and show_caption
        self.scale_border_padding.set_sensitive(enabled and show_caption)
        self.scale_top_padding.set_sensitive(enabled and show_caption)
        self.scale_bottom_padding.set_sensitive(enabled and show_caption)
        self.scale_side_padding.set_sensitive(enabled and show_caption)

        logging.debug('check enable')


# -------------------------------------------------------------------------------
# Run the main class if we are not an import
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    gui = Gui()
    gui.run()

# -)

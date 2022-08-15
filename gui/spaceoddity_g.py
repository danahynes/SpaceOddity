#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity_g.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 08/02/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: get/set font/size
# TODO: use gtkapplication
# TODO: grouping of controls - see settings (deep dark box),
# login manager (light box w/separator)
# TODO: i18n glade file objects with comments
# TODO: tooltips (and i18n *them* with comments)
# TODO: config keys as constants
# TODO: config defaults in shared module
# TODO: object names as constants
# TODO: remove DEBUG

# NB: this script assumes
# config dir,   DONE
# log file,     DONE
# config file,  DONE
# gui dir,
# gui file,
# local_dir,
# and version file all exist

# NB: requires:
# python3-gi
# python3-gi-cairo
# gir1.2-gtk-3.0

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import gettext
import json
import locale
# import logging
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa: E402 (tell linter to ignore order)

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

DEBUG = 1

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

        prog_name = 'spaceoddity'

        # get locations
        home_dir = os.path.expanduser('~')
        conf_dir = os.path.join(home_dir, '.config', prog_name)
        # log_file = os.path.join(conf_dir, f'{prog_name}.log')
        self.conf_file = os.path.join(conf_dir, f'{prog_name}.json')
        gui_dir = os.path.join(conf_dir, 'gui')
        gui_file = os.path.join(gui_dir, f'{prog_name}.glade')
        loc_dir = os.path.join(gui_dir, 'locale')
        vers_file = os.path.join(gui_dir, 'VERSION.txt')

        # create folder if it does not exist
        if not os.path.exists(conf_dir):
            os.mkdir(conf_dir)

        if DEBUG:
            print('home_dir:', home_dir)
            print('conf_dir:', conf_dir)
            # print('log_file:', log_file)
            print('conf_file:', self.conf_file)
            print('gui_dir:', gui_dir)
            print('gui_file:', gui_file)
            print('loc_dir:', loc_dir)
            print('vers_file:', vers_file)

        # # set up logging
        # logging.basicConfig(filename=log_file, filemode='a',
        #                     level=logging.DEBUG,
        #                     format='%(asctime)s - %(message)s')

        # log start
        # logging.debug('-------------------------------------------------------')
        # logging.debug('start gui script')

        # set default config dict
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

        # set up locale
        locale.setlocale(locale.LC_ALL, '')
        locale.bindtextdomain(prog_name, loc_dir)

        # set up gettext
        gettext.bindtextdomain(prog_name, loc_dir)
        gettext.textdomain(prog_name)

        # set up builder and load gui file
        builder = Gtk.Builder()
        builder.set_translation_domain(prog_name)
        builder.add_from_file(gui_file)
        builder.connect_signals(self)

        # get objects in gui
        self.win_main = builder.get_object('win_main')

        # general page
        self.switch_enabled = builder.get_object('switch_enabled')
        self.switch_show_caption = builder.get_object('switch_show_caption')
        self.switch_show_title = builder.get_object('switch_show_title')
        self.switch_show_copyright = builder.get_object('switch_show_copyright')
        self.switch_show_text = builder.get_object('switch_show_text')

        # colors page
        self.btn_fg_color = builder.get_object('btn_fg_color')
        self.slider_fg_transparency = builder.get_object(
            'slider_fg_transparency')
        self.btn_bg_color = builder.get_object('btn_bg_color')
        self.slider_bg_transparency = builder.get_object(
            'slider_bg_transparency')

        # layout page
        self.combo_position = builder.get_object('combo_position')
        self.spin_caption_width = builder.get_object('spin_caption_width')
        self.spin_font_size = builder.get_object('spin_font_size')
        self.spin_corner_radius = builder.get_object('spin_corner_radius')
        self.spin_border_padding = builder.get_object('spin_border_padding')
        self.spin_top_padding = builder.get_object('spin_top_padding')
        self.spin_bottom_padding = builder.get_object('spin_bottom_padding')
        self.spin_side_padding = builder.get_object('spin_side_padding')

        # about dialog
        self.dlg_about = builder.get_object('dlg_about')
        with open(vers_file, 'r') as file:
            version = file.readline()
        self.dlg_about.set_version(version)

        # init the gui from user settings
        self.__load_config()
        self.__load_gui(self.config)

    # --------------------------------------------------------------------------
    # Run the gui
    # --------------------------------------------------------------------------
    def run(self):

        # show the main window
        self.win_main.show_all()

        # run gtk main loop
        Gtk.main()

    # --------------------------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Callback for when the window is closed
    # --------------------------------------------------------------------------
    def win_main_destroy(self, *args):

        # stop the loop and exit script
        Gtk.main_quit()

        # log that we are finished with gui
        # logging.debug('finish gui script')
        # logging.debug('-------------------------------------------------------')

        # quit script
        exit(0)

    # --------------------------------------------------------------------------
    # Callback for when the 'Apply' button is clicked
    # --------------------------------------------------------------------------
    def btn_apply_clicked(self, *args):
        self.__save_gui()
        self.__save_config()
        # TODO: rerun daemon script now

    # --------------------------------------------------------------------------
    # Callback for when the 'Enabled' switch is toggled
    # --------------------------------------------------------------------------
    def switch_enabled_set_state(self, *args):
        self.__check_enable()

    # --------------------------------------------------------------------------
    # Callback for when the 'Caption' switch is toggled
    # --------------------------------------------------------------------------
    def switch_show_caption_set_state(self, *args):
        self.__check_enable()

    # --------------------------------------------------------------------------
    # Callback for 'Reload user settings' menu item is clicked
    # --------------------------------------------------------------------------
    def menu_item_user_clicked(self, *args):
        self.__load_config()
        self.__load_gui(self.config)

    # --------------------------------------------------------------------------
    # Callback for when the 'Load defaults' menu item is clicked
    # --------------------------------------------------------------------------
    def menu_item_defaults_clicked(self, *args):
        self.__load_gui(self.config_defaults)

    # --------------------------------------------------------------------------
    # Callback for when the 'About' menu item is clicked
    # --------------------------------------------------------------------------
    def menu_item_about_clicked(self, *args):

        # run the dailog modally, then hide (not destroy!)
        self.dlg_about.run()
        self.dlg_about.hide()

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Loads the gui state from the specified dict (user or default)
    # --------------------------------------------------------------------------
    def __load_gui(self, dictionary):
        self.switch_enabled.set_active(dictionary['enabled'])
        self.switch_show_caption.set_active(dictionary['show_caption'])
        self.switch_show_title.set_active(dictionary['show_title'])
        self.switch_show_copyright.set_active(dictionary['show_copyright'])
        self.switch_show_text.set_active(dictionary['show_text'])

        color = Gdk.RGBA()
        color.red = dictionary['fg_r']
        color.green = dictionary['fg_g']
        color.blue = dictionary['fg_b']
        self.btn_fg_color.set_rgba(color)

        self.slider_fg_transparency.get_adjustment().set_value(dictionary['fg_a'])

        color = Gdk.RGBA()
        color.red = dictionary['bg_r']
        color.green = dictionary['bg_g']
        color.blue = dictionary['bg_b']
        self.btn_bg_color.set_rgba(color)

        self.slider_bg_transparency.get_adjustment().set_value(dictionary['bg_a'])
        self.combo_position.set_active(dictionary['position'])
        self.spin_caption_width.get_adjustment().set_value(dictionary['caption_width'])
        self.spin_font_size.get_adjustment().set_value(dictionary['font_size'])
        self.spin_corner_radius.get_adjustment().set_value(dictionary['corner_radius'])
        self.spin_border_padding.get_adjustment().set_value(dictionary['border_padding'])
        self.spin_top_padding.get_adjustment().set_value(dictionary['top_padding'])
        self.spin_bottom_padding.get_adjustment().set_value(dictionary['bottom_padding'])
        self.spin_side_padding.get_adjustment().set_value(dictionary['side_padding'])

    # --------------------------------------------------------------------------
    # Saves the gui state to the user dict
    # --------------------------------------------------------------------------
    def __save_gui(self):
        self.config['enabled'] = self.switch_enabled.get_active()
        self.config['show_caption'] = self.switch_show_caption.get_active()
        self.config['show_title'] = self.switch_show_title.get_active()
        self.config['show_copyright'] = self.switch_show_copyright.get_active()
        self.config['show_text'] = self.switch_show_text.get_active()

        color = self.btn_fg_color.get_rgba()
        self.config['fg_r'] = color.red
        self.config['fg_g'] = color.green
        self.config['fg_b'] = color.blue

        self.config['fg_a'] = self.slider_fg_transparency.get_adjustment().get_value()

        color = self.btn_bg_color.get_rgba()
        self.config['bg_r'] = color.red
        self.config['bg_g'] = color.green
        self.config['bg_b'] = color.blue

        self.config['bg_a'] = self.slider_bg_transparency.get_adjustment().get_value()
        self.config['position'] = self.combo_position.get_active()
        self.config['caption_width'] = self.spin_caption_width.get_adjustment().get_value()
        self.config['font_size'] = self.spin_font_size.get_adjustment().get_value()
        self.config['corner_radius'] = self.spin_corner_radius.get_adjustment().get_value()
        self.config['border_padding'] = self.spin_border_padding.get_adjustment().get_value()
        self.config['top_padding'] = self.spin_top_padding.get_adjustment().get_value()
        self.config['bottom_padding'] = self.spin_bottom_padding.get_adjustment().get_value()
        self.config['side_padding'] = self.spin_side_padding.get_adjustment().get_value()

    # --------------------------------------------------------------------------
    # Loads the config dict from a file
    # --------------------------------------------------------------------------
    def __load_config(self):

        # make sure conf file exists
        if not os.path.exists(self.conf_file):
            self.config = dict(self.config_defaults)
            self.__save_config()

        # open the file and read json
        with open(self.conf_file, 'r') as file:
            try:
                self.config = json.load(file)
                # logging.debug('load config file: %s', self.conf_file)
            except json.JSONDecodeError as err:
                self.config = dict(self.config_defaults)
                # logging.debug('could not load json, loading defaults')
                # logging.debug(err)
                self.__save_config()

                if DEBUG:
                    print('error:', err)

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

        # logging.debug('save config file: %s', self.conf_file)

        if DEBUG:
            print('save config:', self.config)

    # --------------------------------------------------------------------------
    # Enables or disables controls based on the state of the first two switches
    # --------------------------------------------------------------------------
    def __check_enable(self):
        enabled = self.switch_enabled.get_active()
        show_caption = self.switch_show_caption.get_active()

        self.switch_show_caption.set_sensitive(enabled)
        self.switch_show_title.set_sensitive(enabled and show_caption)
        self.switch_show_copyright.set_sensitive(enabled and show_caption)
        self.switch_show_text.set_sensitive(enabled and show_caption)
        self.btn_fg_color.set_sensitive(enabled and show_caption)
        self.slider_fg_transparency.set_sensitive(enabled and show_caption)
        self.btn_bg_color.set_sensitive(enabled and show_caption)
        self.slider_bg_transparency.set_sensitive(enabled and show_caption)
        self.combo_position.set_sensitive(enabled and show_caption)
        self.spin_caption_width.set_sensitive(enabled and show_caption)
        self.spin_font_size.set_sensitive(enabled and show_caption)
        self.spin_corner_radius.set_sensitive(enabled) and show_caption
        self.spin_border_padding.set_sensitive(enabled and show_caption)
        self.spin_top_padding.set_sensitive(enabled and show_caption)
        self.spin_bottom_padding.set_sensitive(enabled and show_caption)
        self.spin_side_padding.set_sensitive(enabled and show_caption)


# -------------------------------------------------------------------------------
# Run the main class if we are not an import
# -------------------------------------------------------------------------------
if __name__ == '__main__':
    gui = Gui()
    gui.run()

# -)

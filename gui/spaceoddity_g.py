#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_g.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 08/02/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: seperate this into discrete functions
# TODO: grouping of controls - see settings (deep dark box),
# login manager (light box w/separator)
# TODO: i18n glade file
# TODO: tooltips (and i18n *them*)
# TODO: icon name for main win
# TODO: finish about dialog
# NB: requires:
# python3-gi
# python3-gi-cairo
# gir1.2-gtk-3.0

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import gettext
import json
import locale
import logging
import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

DEBUG = 1

#-------------------------------------------------------------------------------
# Define handler class
#-------------------------------------------------------------------------------

class SignalHandler:

    def win_main_destroy(self, *_):
        Gtk.main_quit()
        exit(0)

    def btn_apply_clicked(self, *_):
        print('btn_apply')

    def switch_enabled_set_state(self, *_):
        print('switch_enabled')

    def switch_caption_set_state(self, *_):
        print('switch_caption')

    def menu_item_user_clicked(self, *_):
        print('menu_item_user')

    def menu_item_defaults_clicked(self, *_):
        print('menu_item_defaults')

    def menu_item_about_clicked(self, *_):
        dlg_about.run()
        dlg_about.hide()
        pass

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
    log_file = os.path.join(conf_dir, f'{prog_name}.log')
    conf_file = os.path.join(conf_dir, f'{prog_name}.json')
    gui_dir = os.path.join(conf_dir, 'gui')
    gui_file = os.path.join(gui_dir, f'{prog_name}.glade')
    loc_dir = os.path.join(gui_dir, 'locale')
    vers_file = os.path.join(gui_dir, 'VERSION.txt')

    # set up logging
    logging.basicConfig(filename = log_file, level = logging.DEBUG,
        format = '%(asctime)s - %(message)s')

    # log start
    logging.debug('------------------------------------------------------')
    logging.debug('Starting gui script')

    if DEBUG:
        print('home_dir:', home_dir)
        print('conf_dir:', conf_dir)
        print('log_file:', log_file)
        print('conf_file:', conf_file)
        print('gui_file:', gui_file)
        print('loc_dir:', loc_dir)

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    # set defaults
    config_defaults = {
        'enabled'           : 1,
        'caption'           : 1,
        'show_title'        : 1,
        'show_copyright'    : 1,
        'show_text'         : 1,
        'position'          : 'BR',
        'fg_r'              : 255,
        'fg_g'              : 255,
        'fg_b'              : 255,
        'fg_a'              : 100,
        'bg_r'              : 0,
        'bg_g'              : 0,
        'bg_b'              : 0,
        'bg_a'              : 75,
        'width'             : 500,
        'font_size'         : 15,
        'corner_radius'     : 15,
        'border'            : 20,
        'top_padding'       : 50,
        'bottom_padding'    : 10,
        'side_padding'      : 10
    }

    # read config file
    with open(conf_file, encoding = 'UTF-8') as file:
        config = json.load(file)

    # get values or defaults
    for key in config_defaults:
        if not key in config.keys():
            config[key] = config_defaults.get(key)

    if DEBUG:
        print('config:', config)

#-------------------------------------------------------------------------------
# Set up the user interface
#-------------------------------------------------------------------------------

    locale.setlocale(locale.LC_ALL, '')
    locale.bindtextdomain(prog_name, loc_dir)

    gettext.bindtextdomain(prog_name, loc_dir)
    gettext.textdomain(prog_name)

    _ = gettext.gettext

    handler = SignalHandler()

    builder = Gtk.Builder()
    builder.set_translation_domain(prog_name)
    builder.add_from_file(gui_file)
    builder.connect_signals(handler)

    win_main = builder.get_object('win_main')

    switch_enabled = builder.get_object('switch_enabled')
    switch_caption = builder.get_object('switch_caption')
    switch_show_title = builder.get_object('switch_show_title')
    switch_show_copyright = builder.get_object('switch_show_copyright')
    switch_show_text = builder.get_object('switch_show_text')

    btn_fg_color = builder.get_object('btn_fg_color')
    slider_fg_transparency =  builder.get_object('slider_fg_transparency')
    btn_bg_color = builder.get_object('btn_bg_color')
    slider_bg_transparency =  builder.get_object('slider_bg_transparency')
    
    combo_position = builder.get_object('combo_position')
    spin_caption_width = builder.get_object('spin_caption_width')
    spin_font_size = builder.get_object('spin_font_size')
    spin_corner_radius = builder.get_object('spin_corner_radius')
    spin_border = builder.get_object('spin_border')
    spin_top_padding = builder.get_object('spin_top_padding')
    spin_bottom_padding = builder.get_object('spin_bottom_padding')
    spin_side_padding = builder.get_object('spin_side_padding')

    global dlg_about # for handler reference
    dlg_about = builder.get_object('dlg_about')
    with open(vers_file, encoding='UTF-8') as file:
        version = file.readline()
    dlg_about.set_version(version)

    win_main.show_all()

    # run gtk main loop
    Gtk.main()

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

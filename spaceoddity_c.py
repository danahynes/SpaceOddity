#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_c.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: defaults

# imports
import configparser
import os

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
    # log_file = os.path.join(conf_dir, f'{prog_name}.log')
    conf_file = os.path.join(conf_dir, f'{prog_name}.conf')


#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    config_parser = configparser.ConfigParser()
    config_parser.read(conf_file)
    config = config_parser[f'{prog_name}']

    position = config['position']
    fg_r = config['fg_r']
    fg_g = config['fg_g']
    fg_b = config['fg_b']
    fg_a = config['fg_a']
    bg_r = config['bg_r']
    bg_g = config['bg_g']
    bg_b = config['bg_b']
    bg_a = config['bg_a']
    width = config['width']
    font_size = config['font_size']
    corner_radius = config['corner_radius']
    border = config['border']
    top_padding = config['top_padding']
    bottom_padding = config['bottom_padding']
    side_padding = config['side_padding']

    print('position:', position)
    print('fg_r:', fg_r)
    print('fg_g:', fg_g)
    print('fg_b:', fg_b)
    print('fg_a:', fg_a)
    print('bg_r:', bg_r)
    print('bg_g:', bg_g)
    print('bg_b:', bg_b)
    print('bg_a:', bg_a)
    print('width:', width)
    print('font_size:', font_size)
    print('corner_radius:', corner_radius)
    print('border:', border)
    print('top_padding:', top_padding)
    print('bottom_padding:', bottom_padding)
    print('side_padding:', side_padding)

# get info file
# install_dir = Home/.spaceoddity
# include grep spaceoddity.conf
# parse that

# Oorig file = first param
# capt_text = second param

# capt_pos = get position (BR)
# capt_color - get color (255,255,255, 1.0)
# capt_ bg_color = bg color (0, 0, 0, 0.75)

# capt width (500)
# capt font size (15)
# capt corner radius (15)
# capt border (20)
# capt top padding (50)
# capt bottom padding (10)
# capt side padding (10)

# text img = text.png
# back img = back.png
# comb img = comb.png
# mask img = mask.png
# capt img = capt.png
# resz img = resz.ext
# temp img = tmp.ext
# log file = log.log


#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

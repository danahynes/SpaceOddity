#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_c.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# NB: requires imagemagick
# NB: this script assumes that
# ~/.config/spaceoddity/spaceoddity.json exists

# imports
import json
import logging
import os
import shlex
import subprocess
import tkinter

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
    data_file = os.path.join(conf_dir, f'{prog_name}.dat')
    log_file = os.path.join(conf_dir, f'{prog_name}.log')
    conf_file = os.path.join(conf_dir, f'{prog_name}.json')

    # set up logging
    logging.basicConfig(filename = log_file, level = logging.DEBUG,
        format = '%(asctime)s - %(message)s')

#-------------------------------------------------------------------------------
# Get data file (the apod data downloaded by main script)
#-------------------------------------------------------------------------------

    # open data file
    with open(data_file, encoding = 'UTF-8') as file:
        apod_data = json.load(file)

    # create a download file path
    pic_url = apod_data['hdurl']
    file_ext = pic_url.split('.')[-1]
    pic_name = f'{prog_name}_wallpaper.{file_ext}'
    pic_path = os.path.join(conf_dir, pic_name)

    # get data for caption
    title = apod_data['title']
    text = apod_data['explanation']

    # print('pic_path:', pic_path)
    # print('title:', title)
    # print('text:', text)
    # exit(0)

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    # set defaults
    config_defaults = {
        'fg_r'              : 255,
        'fg_g'              : 255,
        'fg_b'              : 255,
        'fg_a'              : 100,
        'bg_r'              : 0,
        'bg_g'              : 0,
        'bg_b'              : 0,
        'bg_a'              : 75,
        'position'          : 'BR',
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

    # print(config)
    # exit(0)

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
    position = config['position']
    top_padding = config['top_padding']
    bottom_padding = config['bottom_padding']
    side_padding = config['side_padding']

#-------------------------------------------------------------------------------
# create some file names
#-------------------------------------------------------------------------------

    resz_img = os.path.join(conf_dir, f'{prog_name}.resz.{file_ext}')
    text_img = os.path.join(conf_dir, f'{prog_name}.text.png')
    back_img = os.path.join(conf_dir, f'{prog_name}.back.png')
    comb_img = os.path.join(conf_dir, f'{prog_name}.comb.png')
    mask_img = os.path.join(conf_dir, f'{prog_name}.mask.png')
    capt_img = os.path.join(conf_dir, f'{prog_name}.capt.png')

    # print('resz_img:', resz_img)
    # print('text_img:', text_img)
    # print('back_img:', back_img)
    # print('comb_img:', comb_img)
    # print('mask_img:', mask_img)
    # print('capt_img:', capt_img)
    # exit(0)

#-------------------------------------------------------------------------------
# get picture/screen sizes and scale
#-------------------------------------------------------------------------------

    cmd = f'identify -format %[fx:w] {pic_path}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    pic_w = int(res.decode('UTF-8'))

    cmd = f'identify -format %[fx:h] {pic_path}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    pic_h = int(res.decode('UTF-8'))

    print('pic_w:', pic_w)
    print('pic_h:', pic_h)

    root = tkinter.Tk()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    print('screen w:', screen_w)
    print('screen h:', screen_h)

    scale_w = pic_w/screen_w
    scale_h = pic_h/screen_h

    print('scale_w:', scale_w)
    print('scale_h:', scale_h)

    scale = scale_w
    if scale_h < scale_w:
        scale = scale_h

    new_w = int(pic_w/scale)
    new_h = int(pic_h/scale)

    print('new_w:', new_w)
    print('new_h:', new_h)

#-------------------------------------------------------------------------------
# resize the wallpaper to fill the screen
#-------------------------------------------------------------------------------

    cmd = \
        f'convert \
        {pic_path} \
        -resize {new_w}x{new_h} \
        -extent {new_w}x{new_h} \
        -gravity center \
        {resz_img}'
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    # print(cmd_array)
    # exit(0)

#-------------------------------------------------------------------------------
# The wallpaper has now been resized to "zoom" (i.e. fill the screen at the
# smallest possible size, and yes I realize that's not what most people think
# of when they hear the word "zoom", but in this context it means to scale the
# original picture UP OR DOWN until there is no blank space around the picture.)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# make text png
#-------------------------------------------------------------------------------

# NB: putting spaces in rgba breaks formatting?

    cmd = \
        f'convert \
        -size {width} \
        -pointsize {font_size} \
        -fill rgba({fg_r},{fg_g},{fg_b},({fg_a}/100)) \
        -background none \
        -gravity west \
        caption:\"{title}\n\n{text}\" \
        {text_img}'
    cmd_array = shlex.split(cmd)
    subprocess.call(cmd_array)

    # print(cmd_array)
    # exit(0)

#-------------------------------------------------------------------------------
# get text png size
#-------------------------------------------------------------------------------

    cmd = f'identify -format %[fx:w] {text_img}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    text_w = int(res.decode('UTF-8'))

    cmd = f'identify -format %[fx:h] {text_img}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    text_h = int(res.decode('UTF-8'))

    text_w = (text_w + (int(border) * 2))
    text_h = (text_h + (int(border)* 2))

    # print('text_w:', text_w)
    # print('text_h:', text_h)
    # exit(0)

#-------------------------------------------------------------------------------
# make an image that is text size plus border, using background color
#-------------------------------------------------------------------------------

        #xc:rgba({bg_r},{bg_g},{bg_b},({bg_a}/100)) \
    cmd = \
        f'convert \
        -size {text_w}x{text_h} \
        -extent {text_w}x{text_h} \
        xc:rgba({bg_r},{bg_g},0{bg_b},({bg_a}/100)) \
        {back_img}'

    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    # print(cmd_array)
    # exit(0)

#-------------------------------------------------------------------------------
# Combine text and background image
#-------------------------------------------------------------------------------

    cmd = f'composite \
        -gravity center \
        {text_img} \
        {back_img} \
        {comb_img}'

    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    # exit(0)

#-------------------------------------------------------------------------------
# create a round rect mask
#-------------------------------------------------------------------------------

    cmd = f'convert \
        -size {text_w}x{text_h} \
        xc:none \
        -draw \
        \"roundrectangle \
        0, \
        0, \
        {text_w}, \
        {text_h}, \
        {corner_radius}, \
        {corner_radius}\" \
        {mask_img}'

    cmd_array = shlex.split(cmd)
    subprocess.call(cmd_array)

    # exit(0)

#-------------------------------------------------------------------------------
# merge combination image and mask
#-------------------------------------------------------------------------------

    cmd = f'convert \
        {comb_img} \
        -matte {mask_img} \
        -compose DstIn \
        -composite {capt_img}'


    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    # exit(0)


#-------------------------------------------------------------------------------
# get overhang after scaling the wallpaper
#-------------------------------------------------------------------------------

    x_over = (scale_w - screen_w) / 2
    y_over = (scale_h - screen_h) / 2

#-------------------------------------------------------------------------------
# set the x and y position of the caption
#-------------------------------------------------------------------------------

    x_offset = 0
    y_offset = 0
    x_center = (scale_w - screen_w) / 2
    y_center = (scale_h - screen_h) / 2

    if position == 'TL':
        x_offset = (x_over + side_padding)
        y_offset = (y_over + top_padding)
    elif position == 'TC' :
        pass
    elif position == 'TR' :
        x_offset = scale_w - x_over - text_w - side_padding
        y_offset = y_over + top_padding
    elif position == 'CL' :
        pass
    elif position == 'CC' :
        pass
    elif position == 'CR' :
        pass
    elif position == 'BL' :
        x_offset = x_over + side_padding
        y_offset = scale_h - y_over - text_h - bottom_padding
    elif position == 'BC' :
        pass
    elif position == 'BR' :
        x_offset = scale_w - x_over - text_w - side_padding
        y_offset = scale_h - y_over - text_h - bottom_padding

    print('x_offset:', x_offset)
    print('y_offset:', y_offset)

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

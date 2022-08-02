#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_c.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: convert imagemagick calls to wand
# TODO: put mask/background/text into one operation?
# TODO: fix alpha for foreground/background
    # maybe convert original to png?

# NB: requires :
# imagemagick (sudo apt install imagemagick)
# wand (pip install wand)
# NB: this script assumes that
# ~/.config/spaceoddity/ exists, as well as
# ~/.config/spaceoddity/spaceoddity.dat
# ~/.config/spaceoddity/spaceoddity_desk.???,
# ~/.config/spaceoddity/spaceoddity.json,
# ~/.config/spaceoddity/spaceoddity.log,

# imports
import json
import logging
import os
import shlex
import shutil
import subprocess
import tkinter

DEBUG = 1

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

    # log start
    logging.debug('------------------------------------------------------')
    logging.debug('Starting caption script')

    if DEBUG:
        print('home_dir:', home_dir)
        print('conf_dir:', conf_dir)
        print('data_file:', data_file)
        print('log_file:', log_file)
        print('conf_file:', conf_file)

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    # set defaults
    config_defaults = {
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

    # NB: the int casts here are to make sure someone doesn't manually enter a
    # float into the config file (sanity check)
    position        = config['position'] # position is a string
    fg_r            = int(config['fg_r'])
    fg_g            = int(config['fg_g'])
    fg_b            = int(config['fg_b'])
    fg_a            = int(config['fg_a']) # as a percent (0-100)
    bg_r            = int(config['bg_r'])
    bg_g            = int(config['bg_g'])
    bg_b            = int(config['bg_b'])
    bg_a            = int(config['bg_a']) # as a percent (0-100)
    width           = int(config['width'])
    font_size       = int(config['font_size'])
    corner_radius   = int(config['corner_radius'])
    border          = int(config['border'])
    top_padding     = int(config['top_padding'])
    bottom_padding  = int(config['bottom_padding'])
    side_padding    = int(config['side_padding'])

#-------------------------------------------------------------------------------
# Get data file (the apod data downloaded by main script)
#-------------------------------------------------------------------------------

    # open data file
    with open(data_file, encoding = 'UTF-8') as file:
        apod_data = json.load(file)

    # create a download file path
    pic_url = apod_data['hdurl']
    file_ext = pic_url.split('.')[-1]
    pic_name = f'{prog_name}_desk.{file_ext}'
    pic_path = os.path.join(conf_dir, pic_name)

    # get data for caption
    title = apod_data['title']
    text = apod_data['explanation']

    logging.debug('Got data from JSON file')

    if DEBUG:
        print('pic_path:', pic_path)
        print('title:', title)
        print('text:', text)

#-------------------------------------------------------------------------------
# create some file names
#-------------------------------------------------------------------------------

    orig_img = os.path.join(conf_dir, f'{prog_name}_orig.{file_ext}')
    npng_img = os.path.join(conf_dir, f'{prog_name}_desk.png')
    resz_img = os.path.join(conf_dir, f'{prog_name}_resz.png')
    text_img = os.path.join(conf_dir, f'{prog_name}_text.png')
    back_img = os.path.join(conf_dir, f'{prog_name}_back.png')
    comb_img = os.path.join(conf_dir, f'{prog_name}_comb.png')
    mask_img = os.path.join(conf_dir, f'{prog_name}_mask.png')
    capt_img = os.path.join(conf_dir, f'{prog_name}_capt.png')
    finl_img = os.path.join(conf_dir, f'{prog_name}_finl.png')

    if DEBUG:
        print('orig_img:', orig_img)
        print('npng_img:', npng_img)
        print('resz_img:', resz_img)
        print('text_img:', text_img)
        print('back_img:', back_img)
        print('comb_img:', comb_img)
        print('mask_img:', mask_img)
        print('capt_img:', capt_img)
        print('finl_img:', finl_img)

#-------------------------------------------------------------------------------
# convert original image to backup and store it
#-------------------------------------------------------------------------------

    # first back up original img
    try:
        shutil.copyfile(pic_path, orig_img)
    except shutil.SameFileError:
        pass

    logging.debug('Backed up original image')

    if DEBUG:
        print(f'copying {pic_path} to {orig_img}')

#-------------------------------------------------------------------------------
# convert original image to png
#-------------------------------------------------------------------------------

    # convert it
    cmd = f'convert \
        {pic_path} \
        {npng_img}'
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    logging.debug('Converted original image to PNG')

    if DEBUG:
        print(f'cconvert orig_img: {pic_path} to: {npng_img}')

#-------------------------------------------------------------------------------
# get picture size
#-------------------------------------------------------------------------------

    cmd = \
        f'identify \
        -format \
        %[fx:w] \
        {npng_img}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    pic_w = int(res.decode('UTF-8'))

    cmd = \
        f'identify \
        -format \
        %[fx:h] \
        {npng_img}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    pic_h = int(res.decode('UTF-8'))

    if DEBUG:
        print('pic_w:', pic_w)
        print('pic_h:', pic_h)

#-------------------------------------------------------------------------------
# get screen size
#-------------------------------------------------------------------------------

    root = tkinter.Tk()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    if DEBUG:
        print('screen w:', screen_w)
        print('screen h:', screen_h)

#-------------------------------------------------------------------------------
# get scale
#-------------------------------------------------------------------------------

    # get the scale factor for height and width
    scale_w = pic_w / screen_w
    scale_h = pic_h / screen_h

    if DEBUG:
        print('scale_w:', scale_w)
        print('scale_h:', scale_h)

    # use the smallest scale to get the biggest new dimension
    scale = scale_w if scale_w < scale_h else scale_h

#-------------------------------------------------------------------------------
# get new icture size
#-------------------------------------------------------------------------------

    # get the scaled height/width and make sure it still fills the screen after
    # rounding with an int cast
    tmp_w = int(pic_w / scale)
    new_w = screen_w if tmp_w < screen_w else tmp_w
    tmp_h = int(pic_h / scale)
    new_h = screen_h if tmp_h < screen_h else tmp_h

    if DEBUG:
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

    logging.debug('Resized image')

#-------------------------------------------------------------------------------
# The wallpaper has now been resized to "zoom" (i.e. fill the screen at the
# smallest possible size, and yes I realize that's not what most people think
# of when they hear the word "zoom", but in this context it means to scale the
# original picture UP OR DOWN until there is no blank space around the picture.)
# The reason we do this manually is we have to zoom the picture BEFORE we draw
# the caption, otherwise the system will zoom the caption too, and that will
# make it blurry.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# make text png
#-------------------------------------------------------------------------------

    # NB: putting spaces in rgba breaks formatting?

    # remove border size for text-only png
    tmp_w = width - (border * 2)

    tmp_a = fg_a / 100
    cmd = \
        f'convert \
        -size {tmp_w} \
        -pointsize {font_size} \
        -fill rgba({fg_r},{fg_g},{fg_b},{tmp_a}) \
        -background none \
        -gravity west \
        caption:\"{title}\n\n{text}\" \
        {text_img}'
    cmd_array = shlex.split(cmd)
    subprocess.call(cmd_array)

    logging.debug('Created text image')

#-------------------------------------------------------------------------------
# get text png size
#-------------------------------------------------------------------------------

    cmd = \
        f'identify \
        -format \
        %[fx:w] \
        {text_img}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    text_w = int(res.decode('UTF-8'))

    cmd = \
        f'identify \
        -format \
        %[fx:h] \
        {text_img}'
    cmd_array = cmd.split()
    res = subprocess.check_output(cmd_array)
    text_h = int(res.decode('UTF-8'))

    if DEBUG:
        print('text_w:', text_w)
        print('text_h:', text_h)

#-------------------------------------------------------------------------------
# make an image that is text size plus border, using background color
#-------------------------------------------------------------------------------

    # add the boder back in for the text background size
    text_w = text_w + (border * 2)
    text_h = text_h + (border * 2)

    tmp_a = bg_a / 100
    cmd = \
        f'convert \
        -size {text_w}x{text_h} \
        -extent {text_w}x{text_h} \
        xc:\"rgba({bg_r},{bg_g},{bg_b},{tmp_a})\" \
        {back_img}'
    cmd_array = shlex.split(cmd)
    subprocess.call(cmd_array)

    logging.debug('Created text background')

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

    logging.debug('Created composite text image')

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

    logging.debug('Created rounded mask image')

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

    logging.debug('Created rounded rext text image')

#-------------------------------------------------------------------------------
# set the x and y position of the caption
#-------------------------------------------------------------------------------

    # get the overhang of the image (amount of picture not on screen)
    x_over = (new_w - screen_w) / 2
    y_over = (new_h - screen_h) / 2

    if DEBUG:
        print('x_over:', x_over)
        print('y_over:', y_over)

    # default position is bottom right
    x_pos = new_w - x_over - text_w - side_padding
    y_pos = new_h - y_over - text_h - bottom_padding

    if position == 'TL':
        x_pos = x_over + side_padding
        y_pos = y_over + top_padding
    elif position == 'TC' :
        x_pos = x_over + (screen_w / 2) - (text_w / 2)
        y_pos = y_over + top_padding
    elif position == 'TR' :
        x_pos = new_w - x_over - text_w - side_padding
        y_pos = y_over + top_padding
    elif position == 'CL' :
        x_pos = x_over + side_padding
        y_pos = y_over + (screen_h / 2) - (text_h / 2)
    elif position == 'CC' :
        x_pos = x_over + (screen_w / 2) - (text_w / 2)
        y_pos = y_over + (screen_h / 2) - (text_h / 2)
    elif position == 'CR' :
        x_pos = x_over - screen_w - text_w - side_padding
        y_pos = y_over + (screen_h / 2) - (text_h / 2)
    elif position == 'BL' :
        x_pos = x_over + side_padding
        y_pos = new_h - y_over - text_h - bottom_padding
    elif position == 'BC' :
        x_pos = x_over + (screen_w / 2) - (text_w / 2)
        y_pos = y_over - screen_h - text_h - bottom_padding
    elif position == 'BR' :
        x_pos = new_w - x_over - text_w - side_padding
        y_pos = new_h - y_over - text_h - bottom_padding

    # round off values if division goes wonky
    x_pos = int(x_pos)
    y_pos = int(y_pos)

    if DEBUG:
        print('position:', position)
        print('x_pos:', x_pos)
        print('y_pos:', y_pos)

#-------------------------------------------------------------------------------
# make the final image
#-------------------------------------------------------------------------------

    cmd = f'convert \
        {resz_img} \
        {capt_img} \
        -geometry +{x_pos}+{y_pos} \
        -compose over \
        -composite \
        {finl_img}'
    cmd_array = cmd.split()
    subprocess.call(cmd_array)

    logging.debug('Created final image')


#-------------------------------------------------------------------------------
# delete temps and move final file
#-------------------------------------------------------------------------------

    if not DEBUG:
        os.remove(orig_img)
        os.remove(npng_img)
        os.remove(resz_img)
        os.remove(text_img)
        os.remove(back_img)
        os.remove(comb_img)
        os.remove(mask_img)
        os.remove(capt_img)

    if DEBUG:
        print('pic_path:', pic_path)
        print('finl_img:', finl_img)

    # TODO is weird here, what to convert/replace?
    # cmd = f'convert \
    #     {finl_img} \
    #     {pic_path}'
    # cmd_array = cmd.split()
    # subprocess.call(cmd_array)

    logging.debug('Replaced original imaged with final image')

    if DEBUG:
        print('output file:', pic_path)

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

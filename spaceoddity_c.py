#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_c.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 07/22/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: defaults
# NB: requires imagemagick
# NB: this script assumes that
# ~/.config/spaceoddity/spaceoddity.json exists

# imports
import json
import logging
import os
# import subprocess
# import tkinter

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
        if not (key in config.keys()):
            config[key] = config_defaults.get(key)
        

    print(config)
    exit(0)

    # resz_img = os.path.join(conf_dir, f'{prog_name}.resz.{file_ext}')
    # text_img = os.path.join(conf_dir, f'{prog_name}.text.png')
    # back_img = os.path.join(conf_dir, f'{prog_name}.back.png')
    # comb_img = os.path.join(conf_dir, f'{prog_name}.comb.png')
    # mask_img = os.path.join(conf_dir, f'{prog_name}.mask.png')
    # capt_img = os.path.join(conf_dir, f'{prog_name}.capt.png')

    # print('text_img:', text_img)
    # print('back_img:', back_img)
    # print('comb_img:', comb_img)
    # print('mask_img:', mask_img)
    # print('capt_img:', capt_img)

    # cmd = \
    #     'identify -format %[fx:w] ' + \
    #     pic_path
    # cmd_array = cmd.split()
    # res = subprocess.check_output(cmd_array)
    # pic_w = int(res.decode('utf-8'))

    # cmd = \
    #     'identify -format %[fx:h] ' + \
    #     pic_path
    # cmd_array = cmd.split()
    # res = subprocess.check_output(cmd_array)
    # pic_h = int(res.decode('utf-8'))

    # print('pic_w:', pic_w)
    # print('pic_h:', pic_h)

    # root = tkinter.Tk()
    # screen_w = root.winfo_screenwidth()
    # screen_h = root.winfo_screenheight()


    # print('screen w:', screen_w)
    # print('screen h:', screen_h)

    # scale_w = pic_w/screen_w
    # scale_h = pic_h/screen_h

    # print('scale_w:', scale_w)
    # print('scale_h:', scale_h)

    # scale = scale_w
    # if scale_h < scale_w:
    #     scale = scale_h

    # new_w = int(pic_w/scale)
    # new_h = int(pic_h/scale)

    # print('new_w:', new_w)
    # print('new_h:', new_h)





    # cmd = \
    #     f'convert {pic_path} \
    #     -resize {new_w}x{new_h} \
    #     -extent {new_w}x{new_h} \
    #     -gravity center \
    #     {resz_img}'
    # cmd_array = cmd.split()
    # subprocess.call(cmd_array)

#-------------------------------------------------------------------------------
# The wallpaper has now been resized to "zoom" (i.e. fill the screen at the
# smallest possible size, and yes I realize that's not what most people think
# of when they hear the word "zoom", but in this context it means to scale the
# original picture UP OR DOWN until there is no blank space around the picture.)
#-------------------------------------------------------------------------------






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

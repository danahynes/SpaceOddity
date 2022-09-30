#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: convert_json.py                                      /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/28/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import json
import os


# ------------------------------------------------------------------------------
# Define the main function
# ------------------------------------------------------------------------------
def convert():

    # set the program name for use in file and folder names
    prog_name = 'spaceoddity'

    # get locations
    home_dir = os.path.expanduser('~')
    conf_dir = os.path.join(home_dir, '.config', prog_name)
    conf_path = os.path.join(conf_dir, f'{prog_name}.cfg')

    # if we have an existing conf file
    if os.path.exists(conf_path):

        # set default dict and result
        conf_dict = {}
        res = False

        # read config file
        with open(conf_path, 'r') as file:
            try:
                conf_dict = json.load(file)

                # if it's the old format
                if 'options' in conf_dict.keys():

                    # save current enabled value
                    enabled = conf_dict['options']['enabled']

                    # remove old key
                    conf_dict.pop('options')

                    # create new key and add to dict
                    new_dict = {'enabled': enabled}
                    conf_dict['general'] = new_dict

                    # continue with save
                    res = True

            except Exception as error:
                print(f'could not convert json: {error}')

        # open the file and write json
        if res:
            with open(conf_path, 'w') as file:
                json.dump(conf_dict, file, indent=4)


# ------------------------------------------------------------------------------
# Run the main function if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    convert()

# -)

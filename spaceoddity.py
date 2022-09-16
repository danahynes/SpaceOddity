#!/usr/bin/env python3
# -----------------------------------------------------------------------------#
# Filename: spaceoddity.py                                       /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 09/13/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
# -----------------------------------------------------------------------------#

# TODO: test all conditions (no internet, bad url, etc)
# no conf dir: OK
# No log file: OK
# NEXT: No cfg: doesn't delete old file if no cfg
#   put image in folder, next download, delete all contents of folder
#   then put new image in folder before setting picture-uri
#   or delete everything in .config that isn't spaceoddit.cfg or spaceoddity.log
# bad cfg: OK
# NEXT: old filepath key missing: meh, might not delete old file (see above)
# not enabled: OK
# bad apod url: OK
# no internet: OK
# not image with TEST_IAMGE = 1: OK
# not image with TEST_IAMGE = 0: OK
# bad pic url: OK
# caption no: NA
# caption yes: NA

# NEXT: white line on right of image sometimes (oversizing doesn't help)
# NEXT: print version number in log and terminal
# NEXT: print all log messages also to terminal
# NEXT: check date instead of url
# NEXT: put everything in one folder ~/.spaceoddity

# NB: requires:
# imagemagick (apt)
# wand (pip)

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

# regular imports
from datetime import datetime
import json
import logging
import os
import shlex
import shutil
import subprocess
import urllib.request

import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, Gio # noqa: E402 (ignore import order)

# added imports
from wand.image import Image as wand_image # noqa: E402 (ignore import order)

# ------------------------------------------------------------------------------
# Define the main class
# ------------------------------------------------------------------------------


class Main:

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
        self.conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.conf_path = os.path.join(self.conf_dir, f'{self.prog_name}.cfg')
        log_path = os.path.join(self.conf_dir, f'{self.prog_name}.log')

        # set default config dict
        self.conf_dict_def = {
            'options': {
                'enabled':          1,
                'show_caption':     1
            },
            'apod': {
                'media_type':       '',
                'hdurl':            '',
                'url':              '',
                'title':            '',
                'copyright':        '',
                'explanation':      ''
            },
            'files': {
                'timestamp':        '',
                'old_filepath':     '',
                'filepath':         ''
            },
            'caption_transfer': {
                'pic_w':            0,
                'pic_h':            0,
                'screen_w':         0,
                'screen_h':         0
            },
            'caption_options': {
                'show_title':       1,
                'show_copyright':   1,
                'show_explanation': 1,
                'font_r':           1.0,
                'font_g':           1.0,
                'font_b':           1.0,
                'font_size':        12,
                'bg_r':             0.0,
                'bg_g':             0.0,
                'bg_b':             0.0,
                'bg_a':             75,
                'position':         8,
                'width':            500,
                'radius':           10,
                'border_padding':   10,
                'top_padding':      50,
                'bottom_padding':   10,
                'side_padding':     10
            }
        }

        # user config dict
        self.conf_dict = self.conf_dict_def.copy()

        # create config folder if it does not exist
        os.makedirs(self.conf_dir, exist_ok=True)

        # remove old log file
        if os.path.exists(log_path):
            os.remove(log_path)

        # set up logging
        logging.basicConfig(filename=log_path, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # log start
        logging.debug('=======================================================')
        logging.debug('start main script')

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # init the config dict from user settings
        self.__load_conf()

        # check to see if we are enabled
        options = self.conf_dict['options']
        if options['enabled']:

            # call each step in the process
            self.download_apod_dict()
            self.download_image()
            # NEXT: self.resize_image()
            # NEXT: self.make_caption()
            self.set_image()
            self.delete_old_image()

        else:

            # log the enabled state
            logging.debug('main script disabled')

        # exit gracefully
        self.__do_exit()

    # --------------------------------------------------------------------------
    # Steps
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Get json from api.nasa.gov
    # --------------------------------------------------------------------------
    def download_apod_dict(self):

        # the url to load json from
        apod_url = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'

        # get the json and format it
        try:

            # get the current apod dict
            old_apod_dict = self.conf_dict['apod'].copy()

            # get json from url
            response = urllib.request.urlopen(apod_url)
            response_text = response.read()
            apod_dict = json.loads(response_text)

            # set defaults for any missing keys
            apod_dict_def = self.conf_dict_def['apod']
            for key in apod_dict_def:
                if key not in apod_dict.keys():
                    apod_dict[key] = apod_dict_def[key]

            # apply new dict to config
            self.conf_dict['apod'] = apod_dict

            # log success
            logging.debug('get data from server: %s', apod_dict)

            # check if url is the same
            if self.__check_same_url(old_apod_dict):

                # same url, do nothing
                logging.debug('the apod picture has not changed')
                self.__do_exit()

        except Exception as error:

            # log error
            logging.error('could not get data from server')
            logging.error(error)

            # this is a fatal error
            self.__do_exit()

    # --------------------------------------------------------------------------
    # Get image from api.nasa.gov
    # --------------------------------------------------------------------------
    def download_image(self):

        # make sure it's an image (sometimes it's a video)
        apod_dict = self.conf_dict['apod']
        media_type = apod_dict['media_type']

        # check if today's apod is an image (sometimes it's a video)
        if 'image' in media_type:

            # do the image stuff
            self.__apod_is_image()
        else:

            # do the not image stuff
            self.__apod_is_not_image()

    # --------------------------------------------------------------------------
    # Resize image to fill screen
    # --------------------------------------------------------------------------
    def resize_image(self):

        # get path to downloaded image
        files_dict = self.conf_dict['files']
        pic_path = files_dict['filepath']

        # get original width/height
        old_img = wand_image(filename=pic_path)
        old_w = old_img.width
        old_h = old_img.height

        # get screen size
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        screen_w = geometry.width
        screen_h = geometry.height

        # get the scale factor for height and width
        scale_w = old_w / screen_w
        scale_h = old_h / screen_h

        # use the smallest scale to get the biggest new dimension
        scale = 0
        if scale_w < scale_h:
            scale = scale_w
        else:
            scale = scale_h

        # get the scaled height/width and make sure it still fills the screen
        # after rounding with an int cast
        new_w = int(old_w / scale)
        new_h = int(old_h / scale)

        # resize the image
        old_img.resize(new_w, new_h)

        # save sizes to user dict for caption script
        capt_dict = self.conf_dict['caption']
        capt_dict['pic_w'] = new_w
        capt_dict['pic_h'] = new_h
        capt_dict['screen_w'] = screen_w
        capt_dict['screen_h'] = screen_h

        # log success
        logging.debug('resize image')

    # --------------------------------------------------------------------------
    # Run caption script
    # --------------------------------------------------------------------------
    def make_caption(self):

        # save cofig dict for caption script
        self.__save_conf()

        # get path to caption script
        app_dir = os.path.dirname(os.path.realpath(__file__))
        capt_path = os.path.join(app_dir, f'{self.prog_name}_caption.py')

        # set cmd for running caption
        cmd = capt_path
        cmd_array = shlex.split(cmd)
        subprocess.call(cmd_array)

        logging.debug('make _caption')

    # --------------------------------------------------------------------------
    # Set the wallpaper
    # --------------------------------------------------------------------------
    def set_image(self):

        # get path to downloaded image
        files_dict = self.conf_dict['files']
        pic_path = files_dict['filepath']

        # get system settings
        settings = Gio.Settings.new('org.gnome.desktop.background')

        # set variant for both light and dark themes
        settings.set_string('picture-uri', pic_path)
        settings.set_string('picture-uri-dark', pic_path)

        # save settings
        settings.apply()

        # NB: running from installer doesn't work without this
        settings.sync()

        # log success
        logging.debug('set image: %s', pic_path)

    # --------------------------------------------------------------------------
    # Delete old image
    # --------------------------------------------------------------------------
    def delete_old_image(self):

        # get previous path name
        files_dict = self.conf_dict['files']
        old_image = files_dict['old_filepath']

        # if it exists, delete it
        if os.path.exists(old_image):
            try:
                os.remove(old_image)

                # log success
                logging.debug('remove old image: %s', old_image)

            except Exception as error:

                # log error
                logging.error('could not remove old image')
                logging.error(error)

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Load dictionary data from a file
    # --------------------------------------------------------------------------
    def __load_conf(self):

        # create default dict if file does not exist
        if not os.path.exists(self.conf_path):
            self.conf_dict = self.conf_dict_def.copy()
            self.__save_conf()

        # read config file
        with open(self.conf_path, 'r') as file:
            try:
                self.conf_dict = json.load(file)

                # NB: there is probably a better way to do this
                # get dicts
                dict_def = self.conf_dict_def
                dict_user = self.conf_dict

                # set defaults for any missing sections
                for key in dict_def:
                    if key not in dict_user.keys():
                        dict_user[key] = dict_def[key]

                # do second-level kv defaults
                for key in dict_def:
                    dict_def_2 = dict_def[key]
                    dict_user_2 = dict_user[key]
                    for key in dict_def_2:
                        if key not in dict_user_2.keys():
                            dict_user_2[key] = dict_def_2[key]

                # move filepath for deletiom
                files_dict = self.conf_dict['files']
                files_dict['old_filepath'] = files_dict['filepath']

                # log success
                logging.debug('load conf file: %s', self.conf_dict)

            except Exception as error:

                # if config file error, set defaults and save to file
                self.conf_dict = self.conf_dict_def.copy()
                self.__save_conf()

                # log error
                logging.error('could not load config file, load defaults')
                logging.error(error)

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
    # Get the image when it is an actual image
    # --------------------------------------------------------------------------
    def __apod_is_image(self):

        # get the url to the actual image
        pic_url = self.__get_pic_url()

        # create a download path
        now = datetime.now()
        str_now = now.strftime('%Y%m%d%H%M%S')
        file_ext = pic_url.split('.')[-1]
        pic_name = f'{self.prog_name}_{str_now}.{file_ext}'
        pic_path = os.path.join(self.conf_dir, pic_name)

        # try to download image
        try:

            # download the hi-res image
            urllib.request.urlretrieve(pic_url, pic_path)

            # set pathname
            files_dict = self.conf_dict['files']
            files_dict['filepath'] = pic_path

            # log success
            logging.debug('download image')

        except Exception as error:

            # log error
            logging.error('could not download image')
            logging.error(error)

            # this is a fatal error
            self.__do_exit()

    # --------------------------------------------------------------------------
    # Set some fake data when debugging and APOD is not an image
    # --------------------------------------------------------------------------
    def __apod_is_not_image(self):

        # NB: HOLY FORKING SHIRTBALLS THIS IS AN UGLY HACK!!!
        # but I can't afford to go 24 hours without testing

        # first check if we are running in dev or production
        fake_url = '/home/dana/Documents/Projects/SpaceOddity/_test/test.jpg'

        if os._exists(fake_url):

            fake_exp = 'Lorem ipsum dolor sit amet, consectetur adipiscing '
            fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
            fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
            fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
            fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
            fake_exp += 'dolor in reprehenderit in voluptate velit esse '
            fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
            fake_exp += 'sint occaecat cupidatat non proident, sunt in '
            fake_exp += 'culpa qui officia deserunt mollit anim id est '
            fake_exp += 'laborum.'

            apod_dict = self.conf_dict['apod']
            apod_dict['media_type'] = 'image'
            apod_dict['hdurl'] = fake_url
            apod_dict['url'] = fake_url
            apod_dict['title'] = 'Dummy Title'
            apod_dict['copyright'] = 'Dummy Copyright'
            apod_dict['explanation'] = fake_exp

            # get the url to the actual image
            pic_url = self.__get_pic_url()

            # create a download path
            now = datetime.now()
            str_now = now.strftime('%Y%m%d%H%M%S')
            file_ext = pic_url.split('.')[-1]
            pic_name = f'{self.prog_name}_{str_now}.{file_ext}'
            pic_path = os.path.join(self.conf_dir, pic_name)

            # copy test image (simulates downloading)
            shutil.copy(pic_url, pic_path)

            # set pathname
            files_dict = self.conf_dict['files']
            files_dict['filepath'] = pic_path

            # log success
            logging.debug('make fake image: %s', files_dict)

        else:

            # log failure
            logging.debug('apod is not an image')

            # nothing left to do
            self.__do_exit()

    # --------------------------------------------------------------------------
    # Get the most appropriate url to the full size image
    # --------------------------------------------------------------------------
    def __get_pic_url(self):

        # default return result
        pic_url = ''

        # get current apod dict
        apod_dict = self.conf_dict['apod']

        # get most appropriate URL
        if 'hdurl' in apod_dict.keys():
            pic_url = apod_dict['hdurl']
        elif 'url' in apod_dict.keys():
            pic_url = apod_dict['url']

        return pic_url

    # --------------------------------------------------------------------------
    # Check if new URL is same as old URL
    # --------------------------------------------------------------------------
    def __check_same_url(self, old_dict):

        # default return result
        same_url = False

        # get current apod dict
        curr_dict = self.conf_dict['apod']

        # check if the url is the same
        if 'hdurl' in old_dict.keys() and 'hdurl' in curr_dict.keys():
            if old_dict['hdurl'] == curr_dict['hdurl']:
                same_url = True

        elif 'url' in old_dict.keys() and 'url' in curr_dict.keys():
            if old_dict['url'] == curr_dict['url']:
                same_url = True

        # return the result
        return same_url

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def __do_exit(self):

        # save config dict to file
        self.__save_conf()

        # log that we are finished with script
        logging.debug('exit main script')
        logging.debug('-------------------------------------------------------')

        # quit script
        exit()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main = Main()
    main.run()

# -)

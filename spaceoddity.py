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
#       put image in folder, next download, delete all contents of folder
#       then put new image in folder before setting picture-uri
#       or delete everything in .config that isn't spaceoddit.cfg or spaceoddity.log
# bad cfg: OK
# NEXT: old filepath key missing: meh, might not delete old file (see above)
# not enabled: OK
# bad apod url: OK
# no internet: OK
# not image with DEBUG = 1: OK
# not image with DEBUG = 0: OK
# bad pic url: OK

# NEXT: make a flowchart of code paths and what text/level to log at each step
# NEXT: use rotating logger
# NEXT: log same stuff to log file as console if DEBUG = 1
#       https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout/46098711#46098711
# NEXT: white line on right of image sometimes (oversizing doesn't help)
# NEXT: check date instead of url
# NEXT: put everything in one folder ~/.spaceoddity
# NEXT: should subprocess use run, call, check_call, or check_output?
#       https://docs.python.org/3/library/subprocess.html
# NEXT: run at screen unlock
#       https://unix.stackexchange.com/questions/28181/how-to-run-a-script-on-screen-lock-unlock
#       cron job would only be every hour
# NEXT: run every hour

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from datetime import datetime
from gi.repository.Gio import Settings as gsettings
from urllib import request
import json
import logging
import os
import shutil

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

DEBUG = 1

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
        self.disp_name = 'SpaceOddity'

        # get locations
        home_dir = os.path.expanduser('~')
        self.conf_dir = os.path.join(home_dir, '.config', self.prog_name)
        self.conf_path = os.path.join(self.conf_dir, f'{self.prog_name}.cfg')
        log_path = os.path.join(self.conf_dir, f'{self.prog_name}.log')

        # set default config dict
        self.conf_dict_def = {
            'general': {
                'enabled':          1
            },
            'apod': {
                'media_type':       '',
                'hdurl':            '',
                'url':              '',
            },
            'files': {
                'old_filepath':     '',
                'filepath':         ''
            }
        }

        # user config dict (set to defaults before trying to load file)
        self.conf_dict = self.conf_dict_def.copy()

        # create config folder if it does not exist
        try:
            os.makedirs(self.conf_dir, exist_ok=True)
        except Exception as error:

            # NB: don't log anything here, just print (no logger yet)
            print(f'could not create conf dir: {error}')

            # this is a fatal error
            self.__do_exit()

        # remove old log file
        # NB: don't log anything here, just print (no logger yet)
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
            except Exception as error:
                print(f'could not remove old log file: {error}')

        # set up logging
        logging.basicConfig(filename=log_path, level=logging.DEBUG,
                            format='%(asctime)s [%(levelname)-5s] %(message)s',
                            datefmt='%Y-%m-%d %I:%M:%S %p')

    # --------------------------------------------------------------------------
    # Run the script
    # --------------------------------------------------------------------------
    def run(self):

        # print version number to terminal
        self.__print_version()

        # log start
        self.__logi('=======================================================')
        self.__logi('start main script')

        # init the config dict from user settings
        self.__load_conf()

        # check to see if we are enabled
        general_dict = self.conf_dict['general']
        if general_dict['enabled']:

            # call each step in the process
            self.download_apod_dict()
            self.download_image()
            self.set_image()
            self.delete_old_image()

        else:

            # log the enabled state
            self.__logi('main script disabled')

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
        apod_url = 'https://api.nasa.gov/planetary/apod?api_key='\
            '2h4peiV1XvWqA0bHBxVK21D3QmyBgHtwIyRxo8dm'

        # get the json and format it
        try:

            # get the current apod dict
            old_apod_dict = self.conf_dict['apod'].copy()

            # get json from url
            response = request.urlopen(apod_url)
            response_text = response.read()
            apod_dict = json.loads(response_text)

            # apply new dict to config
            self.conf_dict['apod'] = apod_dict

            # log success
            self.__logd(f'get data from server: {apod_dict}')

            # check if url is the same
            if self.__check_same_url(old_apod_dict):

                # same url, do nothing
                self.__logi('the apod picture has not changed')
                self.__do_exit()

        except Exception as error:

            # log error
            self.__loge(f'could not get data from server: {error}')

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
        if media_type == 'image':

            # do the image stuff
            self.__apod_is_image()
        else:

            # do the not image stuff
            self.__apod_is_not_image()

    # --------------------------------------------------------------------------
    # Set the wallpaper
    # --------------------------------------------------------------------------
    def set_image(self):

        # get path to downloaded image
        files_dict = self.conf_dict['files']
        pic_path = files_dict['filepath']

        # get system settings
        settings = gsettings.new('org.gnome.desktop.background')

        # set variant for both light and dark themes
        settings.set_string('picture-uri', pic_path)
        settings.set_string('picture-uri-dark', pic_path)

        # save settings
        settings.apply()
        settings.sync()

        # log success
        self.__logi('set image')

    # --------------------------------------------------------------------------
    # Delete old image
    # --------------------------------------------------------------------------
    def delete_old_image(self):

        # get previous path name
        files_dict = self.conf_dict['files']
        old_filepath = files_dict['old_filepath']

        # if it exists, delete it
        if os.path.exists(old_filepath):
            try:
                os.remove(old_filepath)

                # log success
                self.__logd(f'delete old image: {old_filepath}')

            except Exception as error:

                # log error
                self.__loge(f'could not delete old image: {error}')

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
                # this is mainly to make sure no one futzed with the config
                # file manually and deleted or mistyped a key
                # also note we don't do any value type checking (i.e. string or
                # int) and no value clamping/validation
                # basically, DON'T EDIT THE FILE BY HAND!!!

                # set defaults for any missing sections

                # get two dicts (src and dst)
                dict_def = self.conf_dict_def
                dict_user = self.conf_dict

                # iterate over src, adding any missing keys to dst
                for key in dict_def.keys():
                    if key not in dict_user.keys():
                        dict_user[key] = dict_def[key]

                # do second-level kv defaults
                for key in dict_def.keys():

                    # get two dicts (src and dst)
                    dict_def_2 = dict_def[key]
                    dict_user_2 = dict_user[key]

                    # iterate over src, adding any missing keys to dst
                    for key in dict_def_2.keys():
                        if key not in dict_user_2.keys():
                            dict_user_2[key] = dict_def_2[key]

                # log success
                self.__logd(f'load conf file: {self.conf_dict}')

            except Exception as error:

                # if config file error, set defaults and save to file
                self.conf_dict = self.conf_dict_def.copy()
                self.__save_conf()

                # log error
                self.__loge(f'could not load conf file: {error}')

    # --------------------------------------------------------------------------
    # Save dictionary data to a file
    # --------------------------------------------------------------------------
    def __save_conf(self):

        # open the file and write json
        with open(self.conf_path, 'w') as file:
            try:
                json.dump(self.conf_dict, file, indent=4)

                # log success
                self.__logd(f'save conf file: {self.conf_dict}')

            except Exception as error:

                # log error
                self.__loge(f'could not save conf file: {error}')

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
            request.urlretrieve(pic_url, pic_path)

            # set pathname
            files_dict = self.conf_dict['files']
            files_dict['old_filepath'] = files_dict['filepath']
            files_dict['filepath'] = pic_path

            # log success
            self.__logd(f'download image: {pic_path}')

        except Exception as error:

            # log error
            self.__loge(f'could not download image: {error}')

            # this is a fatal error
            self.__do_exit()

    # --------------------------------------------------------------------------
    # Set some fake data when debugging and APOD is not an image
    # --------------------------------------------------------------------------
    def __apod_is_not_image(self):

        # log failure
        self.__logi('apod is not an image')

        if not DEBUG:

            # nothing left to do
            self.__do_exit()

        else:

            # NB: HOLY FORKING SHIRTBALLS THIS IS AN UGLY HACK!!!
            # but I can't afford to go 24 hours without testing

            # set picture url
            fake_url = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '_test/test.jpg')

            apod_dict = self.conf_dict['apod']
            apod_dict['media_type'] = 'image'
            apod_dict['hdurl'] = fake_url
            apod_dict['url'] = fake_url

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
            files_dict['old_filepath'] = files_dict['filepath']
            files_dict['filepath'] = pic_path

            # log success
            self.__logd(f'make fake image: {files_dict}')

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

        # return the result
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
        if not DEBUG:
            return same_url
        else:
            return False

    # --------------------------------------------------------------------------
    # Print debug message to log file and terminal
    # --------------------------------------------------------------------------
    def __logd(self, msg):
        logging.debug(msg)
        print('DEBUG:', msg)

    # --------------------------------------------------------------------------
    # Print error message to log file and terminal
    # --------------------------------------------------------------------------
    def __loge(self, msg):
        logging.error(msg)
        print('ERROR:', msg)

    # --------------------------------------------------------------------------
    # Print info message to log file and terminal
    # --------------------------------------------------------------------------
    def __logi(self, msg):
        logging.info(msg)
        print('INFO :', msg)

    # --------------------------------------------------------------------------
    # Print version number to terminal
    # --------------------------------------------------------------------------
    def __print_version(self):

        # get current dir
        src_dir = os.path.dirname(os.path.abspath(__file__))

        # get VERSION file
        ver_path = os.path.join(src_dir, 'VERSION')

        # read version number
        with open(ver_path, 'r') as file:
            try:
                ver_num = file.readline()
                ver_str = f'{self.disp_name} version {ver_num}'

                # log success
                self.__logi(ver_str)

            except Exception as error:

                # log error
                self.__loge(f'could not load VERSION file: {error}')

    # --------------------------------------------------------------------------
    # Gracefully exit the script when we are done or on failure
    # --------------------------------------------------------------------------
    def __do_exit(self):

        # save config dict to file
        self.__save_conf()

        # log that we are finished with script
        self.__logi('exit main script')
        self.__logi('-------------------------------------------------------')

        # quit script
        exit()


# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    main = Main()
    main.run()

# -)

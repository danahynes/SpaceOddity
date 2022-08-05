#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: spaceoddity_g.py                                     /          \  #
# Project : SpaceOddity                                         |     ()     | #
# Date    : 08/02/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# TODO: i18n glade file
# TODO: tooltips (and i18n *them*)
# TODO: icon name for main win
# TODo: finish about dialog

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

# import gettext
# import gi
import json
# import locale
import logging
import os

# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

DEBUG = 1

#-------------------------------------------------------------------------------
# Define handler class
#-------------------------------------------------------------------------------

class SignalHandler:

    def win_destroy(self, *args):
        # Gtk.main_quit()
        exit(0)

    # def onClickApp(self, *args):

    #     # I18N: This is a comment for the file chooser dialog title
    #     fileChooser = Gtk.FileChooserDialog(title = _('Choose an app'))
    #     fileChooser.add_buttons(Gtk.STOCK_CANCEL,
    #                             Gtk.ResponseType.CANCEL,
    #                             Gtk.STOCK_OK,
    #                             Gtk.ResponseType.OK)
    #     fileChooser.set_default_response(Gtk.ResponseType.OK)
    #     if fileChooser.run() == Gtk.ResponseType.OK:
    #         nameApp = fileChooser.get_filename()
    #         entryApp.set_text(nameApp)
    #     fileChooser.destroy()

    # def onClickIcon(self, *args):
    #     # I18N: this is a comment for the file chooser title
    #     fileChooser = Gtk.FileChooserDialog(title = _('Choose an icon'))
    #     fileChooser.add_buttons(Gtk.STOCK_CANCEL,
    #                             Gtk.ResponseType.CANCEL,
    #                             Gtk.STOCK_OK,
    #                             Gtk.ResponseType.OK)
    #     fileChooser.set_default_response(Gtk.ResponseType.OK)
    #     if fileChooser.run() == Gtk.ResponseType.OK:
    #         nameIcon = fileChooser.get_filename()
    #         entryIcon.set_text(nameIcon)
    #     fileChooser.destroy()

    # def onClickOK(self, button):
    #     strName = entryName.get_text()
    #     if strName == '':
    #         msgBox = Gtk.MessageDialog(message_type = Gtk.MessageType.ERROR,
    #                                    text = _('Name must not be empty'),
    #                                    buttons = Gtk.ButtonsType.OK)
    #         msgBox.run()
    #         msgBox.destroy()
    #         window.set_focus(entryName)
    #         return

    #     strComment = entryComment.get_text()
    #     strCat = entryCat.get_text()

    #     strApp = entryApp.get_text()
    #     if strApp == '':
    #         msgBox = Gtk.MessageDialog(message_type = Gtk.MessageType.ERROR,
    #                                    text = _('Application must not be empty'),
    #                                    buttons = Gtk.ButtonsType.OK)
    #         msgBox.run()
    #         msgBox.destroy()
    #         window.set_focus(entryApp)
    #         return
    #     strApp = fixPath(strApp)

    #     strPath = path.dirname(strApp)

    #     strIcon = entryIcon.get_text()
    #     # if strIcon == '':
    #     #     msgBox = Gtk.MessageDialog(message_type = Gtk.MessageType.ERROR,
    #     #                                text = _('Icon must not be empty'),
    #     #                                buttons = Gtk.ButtonsType.OK)
    #     #     msgBox.run()
    #     #     msgBox.destroy()
    #     #     window.set_focus(entryIcon)
    #     #     return
    #     strIcon = fixPath(strIcon)

    #     boolTerm = switchTerm.get_active()
    #     strTerm = '{}'.format(boolTerm)
    #     strTerm = strTerm.lower()

    #     fileName = strName.replace(' ', '-')
    #     fileName = fileName.lower()
    #     if fileName[:1].isdigit():
    #         fileName = '_' + fileName
    #     fileName = fileName + '.desktop'

    #     strCreated = _('Created by')
    #     now = datetime.now()
    #     # TODO: localize (NOT i18n) date/time
    #     strFormat = '%m/%d/%Y %H:%M:%S'
    #     strFormat = '%x %X'
    #     strNow = now.strftime(strFormat)

    #     # https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
    #     with open(fileName, 'w') as file:
    #         file.write('# {0} LaunchCode {1}\n'.format(strCreated, strNow))
    #         file.write('[Desktop Entry]\n')
    #         file.write('Version=1.0\n')
    #         file.write('Encoding=UTF-8\n')
    #         file.write('Type=Application\n')
    #         file.write('Name={}\n'.format(strName))
    #         file.write('Comment={}\n'.format(strComment))
    #         file.write('Categories={}\n'.format(strCat))
    #         file.write('Exec={}\n'.format(strApp))
    #         file.write('Icon={}\n'.format(strIcon))
    #         file.write('Terminal={}\n'.format(strTerm))
    #         # NB this will localize using the domain???
    #         file.write('X-Ubuntu-Gettext-Domain=s{}\n'.format(strName))

    #     home = path.expanduser('~')
    #     filePath = path.join(home, '.local/share/applications', fileName)
    #     cmd = 'mv {0} {1}'.format(fileName, filePath)
    #     if switchAll.get_active():
    #         filePath = path.join('/usr/share/applications', fileName)
    #         cmd = 'pkexec mv {0} {1}'.format(fileName, filePath)
    #     cmdArray = cmd.split(' ')

    #     if DEBUG == 1:
    #         print(cmdArray)
    #     else:
    #         subprocess.call(cmdArray)

    #     Gtk.main_quit()

    # def onClickCancel(self, button):
    #     Gtk.main_quit()

    # def onClickAbout(self, button):
    #     with open('../VERSION', 'r') as file:
    #         version = file.readline()
    #     dialogAbout.set_version(version)
    #     dialogAbout.run()
    #     dialogAbout.hide()

    #pass

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
    # TODO: gui_file = os.path.join('/usr/bin', f'{prog_name}.glade')
    gui_file = os.path.join(conf_dir, f'{prog_name}.glade')
    
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

#-------------------------------------------------------------------------------
# Get config values from config file
#-------------------------------------------------------------------------------

    # set defaults
    config_defaults = {
        'enabled' : 1,
        'caption' : 1,
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

    # the only keys we care about
    #enabled = bool(config['enabled'])
    #caption = bool(config['caption']



    # gui_path = path.dirname(path.abspath(__file__))
    # locale_path = path.join(conf_dir, 'locale')

    # locale.setlocale(locale.LC_ALL, '')
    # locale.bindtextdomain(appName, localePath)

    # gettext.bindtextdomain(appName, localePath)
    # gettext.textdomain(appName)

    # _ = gettext.gettext

    handler = SignalHandler()

    # builder = Gtk.Builder()
    # builder.set_translation_domain(appName)
    # builder.add_from_file(f'{prog_name}.glade')
    # builder.connect_signals(handler)

    # window = builder.get_object('so_options')
    # witch_enabled = builder.get_object('so_options_nb_general_switch_enabled')
    # switch_caption = builder.get_object('so_options_nb_general_switch_caption')
    
    # entryName = builder.get_object('entryName')
    # entryComment = builder.get_object('entryComment')
    # entryCat = builder.get_object('entryCat')
    # entryApp = builder.get_object('entryApp')
    # entryIcon = builder.get_object('entryIcon')
    # switchTerm = builder.get_object('switchTerm')
    # switchAll = builder.get_object('switchAll')
    # dialogAbout = builder.get_object('dialogAbout')

    # window.show_all()

    # run gtk main loop
    # Gtk.main()

#-------------------------------------------------------------------------------
# Run the main function if we are not an import
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# -)

#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: launchcode.py                                        /          \  #
# Project : LaunchCode                                          |     ()     | #
# Date    : 05/25/2022                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : GPLv3                                                \          /  #
#------------------------------------------------------------------------------#

# TODO: path out, keywords in
# TODO: categories and keywords must end with semicolon
# TODO: get rid of fixPath
# TODO: code comments from apod_linux git repo
# TODO: i18n

# TODO: pyinstaller
# TODO: make checklist for all this stuff (or template project)
# I18N: 
DEBUG = 1

import gettext
import gi
import locale
import subprocess

from datetime import datetime
from os import path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def fixPath(path_):

    """
    isabs - returns true if the path starts with '/'
    abspath - if starts with slash, use it - else use cwd
        also normalize
    normpath - condenses multiple slashed and follows (and removes) . and ..
        only in the middle i.e. 'foo/../bar' becomes 'bar' (no leading slash)
        if the path was not already absolute, the result is not absolute
    realpath - if starts with slash, use it - else use cwd
        also normalize
        also follow symbolic links
    """
    if path_ == '':
        return path_

    if path.isabs(path_):
        path_ = path.realpath(path_)
    else:
        path_ = path.normpath(path_)

    return path_

class SignalHandler:

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onClickApp(self, *args):
        # I18N: This is a comment for the file chooser dialog title
        fileChooser = Gtk.FileChooserDialog(title = _('Choose an app'))
        fileChooser.add_buttons(Gtk.STOCK_CANCEL,
                                Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK,
                                Gtk.ResponseType.OK)
        fileChooser.set_default_response(Gtk.ResponseType.OK)
        if fileChooser.run() == Gtk.ResponseType.OK:
            nameApp = fileChooser.get_filename()
            entryApp.set_text(nameApp)
        fileChooser.destroy()

    def onClickIcon(self, *args):
        fileChooser = Gtk.FileChooserDialog(title = _('Choose an icon'))
        fileChooser.add_buttons(Gtk.STOCK_CANCEL,
                                Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK,
                                Gtk.ResponseType.OK)
        fileChooser.set_default_response(Gtk.ResponseType.OK)
        if fileChooser.run() == Gtk.ResponseType.OK:
            nameIcon = fileChooser.get_filename()
            entryIcon.set_text(nameIcon)
        fileChooser.destroy()

    def onClickOK(self, button):
        strName = entryName.get_text()
        if strName == '':
            msgBox = Gtk.MessageDialog(message_type = Gtk.MessageType.ERROR,
                                       text = _('Name must not be empty'),
                                       buttons = Gtk.ButtonsType.OK)
            msgBox.run()
            msgBox.destroy()
            window.set_focus(entryName)
            return

        strComment = entryComment.get_text()
        strCat = entryCat.get_text()

        strApp = entryApp.get_text()
        if strApp == '':
            msgBox = Gtk.MessageDialog(message_type = Gtk.MessageType.ERROR,
                                       text = _('Application must not be empty'),
                                       buttons = Gtk.ButtonsType.OK)
            msgBox.run()
            msgBox.destroy()
            window.set_focus(entryApp)
            return
        strApp = fixPath(strApp)

        strPath = path.dirname(strApp)

        strIcon = entryIcon.get_text()
        # if strIcon == '':
        #     msgBox = Gtk.MessageDialog(message_type = Gtk.MessageType.ERROR,
        #                                text = _('Icon must not be empty'),
        #                                buttons = Gtk.ButtonsType.OK)
        #     msgBox.run()
        #     msgBox.destroy()
        #     window.set_focus(entryIcon)
        #     return
        strIcon = fixPath(strIcon)

        boolTerm = switchTerm.get_active()
        strTerm = '{}'.format(boolTerm)
        strTerm = strTerm.lower()

        fileName = strName.replace(' ', '-')
        fileName = fileName.lower()
        if fileName[:1].isdigit():
            fileName = '_' + fileName
        fileName = fileName + '.desktop'

        strCreated = _('Created by')
        now = datetime.now()
        # TODO: localize (NOT i18n) date/time
        strFormat = '%m/%d/%Y %H:%M:%S'
        strFormat = '%x %X'
        strNow = now.strftime(strFormat)

        # https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
        with open(fileName, 'w') as file:
            file.write('# {0} LaunchCode {1}\n'.format(strCreated, strNow))
            file.write('[Desktop Entry]\n')
            file.write('Version=1.0\n')
            file.write('Encoding=UTF-8\n')
            file.write('Type=Application\n')
            file.write('Name={}\n'.format(strName))
            file.write('Comment={}\n'.format(strComment))
            file.write('Categories={}\n'.format(strCat))
            file.write('Exec={}\n'.format(strApp))
            file.write('Icon={}\n'.format(strIcon))
            file.write('Terminal={}\n'.format(strTerm))
            # NB this will localize using the domain???
            file.write('X-Ubuntu-Gettext-Domain=s{}\n'.format(strName))

        home = path.expanduser('~')
        filePath = path.join(home, '.local/share/applications', fileName)
        cmd = 'mv {0} {1}'.format(fileName, filePath)
        if switchAll.get_active():
            filePath = path.join('/usr/share/applications', fileName)
            cmd = 'pkexec mv {0} {1}'.format(fileName, filePath)
        cmdArray = cmd.split(' ')

        if DEBUG == 1:
            print(cmdArray)
        else:
            subprocess.call(cmdArray)

        Gtk.main_quit()

    def onClickCancel(self, button):
        Gtk.main_quit()

    def onClickAbout(self, button):
        with open('../VERSION', 'r') as file:
            version = file.readline()
        dialogAbout.set_version(version)
        dialogAbout.run()
        dialogAbout.hide()

appName = 'launchcode'
appPath = path.dirname(path.abspath(__file__))
localePath = path.join(appPath, '../locale')

locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(appName, localePath)

gettext.bindtextdomain(appName, localePath)
gettext.textdomain(appName)

_ = gettext.gettext

handler = SignalHandler()

builder = Gtk.Builder()
builder.set_translation_domain(appName)
builder.add_from_file('launchcode.glade')
builder.connect_signals(handler)

window = builder.get_object('mainWindow')
entryName = builder.get_object('entryName')
entryComment = builder.get_object('entryComment')
entryCat = builder.get_object('entryCat')
entryApp = builder.get_object('entryApp')
entryIcon = builder.get_object('entryIcon')
switchTerm = builder.get_object('switchTerm')
switchAll = builder.get_object('switchAll')
dialogAbout = builder.get_object('dialogAbout')

window.show_all()

Gtk.main()

# -)
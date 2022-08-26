#!/usr/bin/env python3
#------------------------------------------------------------------------------#
# Filename: apod_linux_config.py                                 /          \  #
# Project : APOD_Linux                                          |     ()     | #
# Date    : 06/23/2021                                          |            | #
# Author  : Dana Hynes                                          |   \____/   | #
# License : WTFPLv2                                              \          /  #
#------------------------------------------------------------------------------#

# imports
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import logging
import os
import subprocess

str_prog_name = "apod_linux"

# find the config file
home_dir = os.path.expanduser("~")
pic_dir = os.path.join(home_dir, "." + str_prog_name)
conf_file = os.path.join(pic_dir, str_prog_name + ".conf")

# get log file name`
log_file = os.path.join(pic_dir, str_prog_name + ".log")

# set up logging
logging.basicConfig(filename = log_file, level = logging.DEBUG,
        format = "%(asctime)s - %(message)s")

# set defaults for first tab
def_enabled = True
def_delay = 30
def_caption = True
def_position = "BR"

# set defaults for second tab
def_text_r = 255
def_text_g = 255
def_text_b = 255
def_text_a = 100
def_bg_r = 0
def_bg_g = 0
def_bg_b = 0
def_bg_a = 75

# set defaults for third tab
def_width = 500
def_font_size = 15
def_corner = 15
def_border = 20
def_top_pad = 50
def_bottom_pad = 10
def_side_pad = 10

# default strings
str_title = "APOD_Linux"

str_label_enabled = "Enable " + str_title + ":"
str_tooltip_enabled = "Enables or disables the " + str_title + " program"
str_label_delay = "Delay (0-60):"
str_tooltip_delay = "How long to wait (in seconds) for an internet connection \
before downloading"
str_label_caption = "Use caption:"
str_tooltip_caption = "Enables or disables the caption on top of the wallpaper"
str_tab_general = "General"

str_label_text = "<b>Text</b>"
str_label_text_r = "Red (0-255):"
str_tooltip_text_r = "The red value for the caption text"
str_label_text_g = "Green (0-255):"
str_tooltip_text_g = "The green value for the caption text"
str_label_text_b = "Blue (0-255):"
str_tooltip_text_b = "The blue value for the caption text"
str_label_text_a = "Alpha % (0-100):"
str_tooltip_text_a = "The alpha (transparency) value for the caption text"
str_label_bg = "<b>Background</b>"
str_label_bg_r = "Red (0-255):"
str_tooltip_bg_r = "The red value for the caption background"
str_label_bg_g = "Green (0-255):"
str_tooltip_bg_g = "The green value for the caption background"
str_label_bg_b = "Blue (0-255):"
str_tooltip_bg_b = "The blue value for the caption background"
str_label_bg_a = "Alpha % (0-100):"
str_tooltip_bg_a = "The alpha (transparency) value for the caption background"
str_tab_colors = "Colors"

str_label_position = "Position:"
str_tooltip_position = "The position of the caption relative to the screen"
str_label_width = "Width (0-1000):"
str_tooltip_width = "The width of the caption bubble"
str_label_font_size = "Font size (0-50):"
str_tooltip_font_size = "The font size of the caption"
str_label_corner = "Corner radius (0-50):"
str_tooltip_corner = "The corner radius of the caption bubble"
str_label_border = "Border (0-50):"
str_tooltip_border = "The spacing between the caption text and the background \
bubble"
str_label_top_pad = "Top padding (0-100):"
str_tooltip_top_pad = "The spacing between the caption and the top of the \
screen"
str_label_bottom_pad = "Bottom padding (0-100):"
str_tooltip_bottom_pad = "The spacing between the caption and the bottom of \
the screen"
str_label_side_pad = "Side padding (0-100):"
str_tooltip_side_pad = "The spacing between the caption and the sides of the \
screen"
str_tab_sizes = "Sizes"

str_button_ok = "OK"
str_button_cancel = "Cancel"
str_button_apply = "Apply"

str_tl = "Top Left"
str_tr = "Top Right"
str_bl = "Bottom Left"
str_br = "Bottom Right"
str_c = "Center"

# map short names to display strings
position_map = {
    "TL" : str_tl,
    "TR" : str_tr,
    "BL" : str_bl,
    "BR" : str_br,
    "C"  : str_c
}

run_prog_cmd = "python3 /usr/bin/apod_linux.py & disown"

# the main window class
class MyWindow(Gtk.Window):

    # constructor
    def __init__(self):

        # call super constructor
        Gtk.Window.__init__(self, title=str_title)

        # the padding between the window edge and the content
        self.set_border_width(20)

        # set new width and default (fit) height
        self.set_default_size(600, -1)

        # don't allow resizing of window
        self.set_resizable(False)

        # create the stack BEFORE switcher and set props
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.NONE)

        # create the switcher and attach stack
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)

        # create a box for the switcher that keeps it centered horizontally
        # resize box to fill parent but do not resize child (switcher)
        # in an hbox, the child automatically fills vertically but is centered
        # horizontally
        hbox_switcher = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_switcher.pack_start(stack_switcher, True, False, 0)

        # the first tab

        # create a grid with inter-spacig
        grid_general = Gtk.Grid()
        grid_general.set_row_spacing(20)
        grid_general.set_column_spacing(20)

        # add a label and switch
        label_enabled = Gtk.Label(label=str_label_enabled)
        label_enabled.set_alignment(1, 0)
        grid_general.attach(label_enabled, 0, 0, 1, 1)

        self.switch_enabled = Gtk.Switch()
        self.switch_enabled.connect("notify::active",
                self.switch_enabled_clicked)
        self.switch_enabled.set_tooltip_text(str_tooltip_enabled)

        hbox_enabled = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        hbox_enabled.pack_start(self.switch_enabled, False, False, 0)

        grid_general.attach(hbox_enabled, 1, 0, 1, 1)

        # add a label
        label_delay = Gtk.Label(label=str_label_delay)
        label_delay.set_alignment(1, 0)
        grid_general.attach(label_delay, 0, 1, 1, 1)

        # add a spinbox that grows horizontally
        adj_delay = Gtk.Adjustment(
                0.0,
                0.0,
                60.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_delay = Gtk.SpinButton(adjustment=adj_delay, hexpand=True)
        self.spin_delay.set_numeric(True)
        self.spin_delay.set_tooltip_text(str_tooltip_delay)
        grid_general.attach(self.spin_delay, 1, 1, 1, 1)

        # add a label and switch
        label_caption = Gtk.Label(label=str_label_caption)
        label_caption.set_alignment(1, 0)
        grid_general.attach(label_caption, 0, 2, 1, 1)

        self.switch_caption = Gtk.Switch()
        self.switch_caption.connect("notify::active",
                self.switch_caption_clicked)
        self.switch_caption.set_tooltip_text(str_tooltip_caption)

        hbox_caption = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        hbox_caption.pack_start(self.switch_caption, False, False, 0)

        grid_general.attach(hbox_caption, 1, 2, 1, 1)

        label_position = Gtk.Label(label=str_label_position)
        label_position.set_alignment(1, 0)
        grid_general.attach(label_position, 0, 3, 1, 1)

        # combos can take keys and vals and will only diplay vals
        self.combo_position = Gtk.ComboBoxText()
        self.combo_position.set_tooltip_text(str_tooltip_position)
        grid_general.attach(self.combo_position, 1, 3, 1, 1)
        for key, val in position_map.items():
            self.combo_position.append(key, val)

        # add the grid to the stack with a name and a title
        stack.add_titled(grid_general, "general", str_tab_general)

        # the second tab

        # create a grid with inter-spacig
        grid_colors = Gtk.Grid()
        grid_colors.set_row_spacing(20)
        grid_colors.set_column_spacing(20)

        label_text = Gtk.Label()
        label_text.set_markup(str_label_text)

        sep_text = Gtk.HSeparator()

        # a box to vertically center the separator
        # resize the box to fill the cell but do not resize child
        # in a vbox, the child automatically fills the width but is centered
        # vertically
        vbox_sep_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_sep_text.pack_start(sep_text, True, False, 0)

        # a box to contain label and separator box
        # label is F, F to make it as small as possible
        # box is T, T to make it as big as possible
        hbox_text = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox_text.pack_start(label_text, False, False, 0)
        hbox_text.pack_start(vbox_sep_text, True, True, 0)
        grid_colors.attach(hbox_text, 0, 0, 2, 1)

        # right-align labels, set spin min/max, and numeric only
        label_text_r = Gtk.Label(label=str_label_text_r)
        label_text_r.set_alignment(1, 0)
        grid_colors.attach(label_text_r, 0, 1, 1, 1)

        adj_text_r = Gtk.Adjustment(
                0.0,
                0.0,
                255.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_text_r = Gtk.SpinButton(adjustment=adj_text_r, hexpand=True)
        self.spin_text_r.set_numeric(True)
        self.spin_text_r.set_tooltip_text(str_tooltip_text_r)
        grid_colors.attach(self.spin_text_r, 1, 1, 1, 1)

        label_text_g = Gtk.Label(label=str_label_text_g)
        label_text_g.set_alignment(1, 0)
        grid_colors.attach(label_text_g, 0, 2, 1, 1)

        adj_text_g = Gtk.Adjustment(
                0.0,
                0.0,
                255.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_text_g = Gtk.SpinButton(adjustment=adj_text_g, hexpand=True)
        self.spin_text_g.set_numeric(True)
        self.spin_text_g.set_tooltip_text(str_tooltip_text_g)
        grid_colors.attach(self.spin_text_g, 1, 2, 1, 1)

        label_text_b = Gtk.Label(label=str_label_text_b)
        label_text_b.set_alignment(1, 0)
        grid_colors.attach(label_text_b, 0, 3, 1, 1)

        adj_text_b = Gtk.Adjustment(
                0.0,
                0.0,
                255.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_text_b = Gtk.SpinButton(adjustment=adj_text_b, hexpand=True)
        self.spin_text_b.set_numeric(True)
        self.spin_text_b.set_tooltip_text(str_tooltip_text_b)
        grid_colors.attach(self.spin_text_b, 1, 3, 1, 1)

        label_text_a = Gtk.Label(label=str_label_text_a)
        label_text_a.set_alignment(1, 0)
        grid_colors.attach(label_text_a, 0, 4, 1, 1)

        adj_text_a = Gtk.Adjustment(
                0.0,
                0.0,
                100.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_text_a = Gtk.SpinButton(adjustment=adj_text_a, hexpand=True)
        self.spin_text_a.set_numeric(True)
        self.spin_text_a.set_tooltip_text(str_tooltip_text_a)
        grid_colors.attach(self.spin_text_a, 1, 4, 1, 1)

        label_bg = Gtk.Label()
        label_bg.set_markup(str_label_bg)

        sep_bg = Gtk.HSeparator()

        # a box to vertically center the separator
        # resize the box to fill the cell but do not resize child
        # in a vbox, the child automatically fills the width but is centered
        # vertically
        vbox_sep_bg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_sep_bg.pack_start(sep_bg, True, False, 0)

        # a box to contain label and separator box
        # label is F, F to make it as small as possible
        # box is T, T to make it as big as possible
        hbox_bg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox_bg.pack_start(label_bg, False, False, 0)
        hbox_bg.pack_start(vbox_sep_bg, True, True, 0)
        grid_colors.attach(hbox_bg, 0, 5, 2, 1)

        # right-align labels, set spin min/max, and numeric only
        label_bg_r = Gtk.Label(label=str_label_bg_r)
        label_bg_r.set_alignment(1, 0)
        grid_colors.attach(label_bg_r, 0, 6, 1, 1)

        adj_bg_r = Gtk.Adjustment(
                0.0,
                0.0,
                255.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_bg_r = Gtk.SpinButton(adjustment=adj_bg_r, hexpand=True)
        self.spin_bg_r.set_numeric(True)
        self.spin_bg_r.set_tooltip_text(str_tooltip_bg_r)
        grid_colors.attach(self.spin_bg_r, 1, 6, 1, 1)

        label_bg_g = Gtk.Label(label=str_label_bg_g)
        label_bg_g.set_alignment(1, 0)
        grid_colors.attach(label_bg_g, 0, 7, 1, 1)

        adj_bg_g = Gtk.Adjustment(
                0.0,
                0.0,
                255.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_bg_g = Gtk.SpinButton(adjustment=adj_bg_g, hexpand=True)
        self.spin_bg_g.set_numeric(True)
        self.spin_bg_g.set_tooltip_text(str_tooltip_bg_g)
        grid_colors.attach(self.spin_bg_g, 1, 7, 1, 1)

        label_bg_b = Gtk.Label(label=str_label_bg_b)
        label_bg_b.set_alignment(1, 0)
        grid_colors.attach(label_bg_b, 0, 8, 1, 1)

        adj_bg_b = Gtk.Adjustment(
                0.0,
                0.0,
                255.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_bg_b = Gtk.SpinButton(adjustment=adj_bg_b, hexpand=True)
        self.spin_bg_b.set_numeric(True)
        self.spin_bg_b.set_tooltip_text(str_tooltip_bg_b)
        grid_colors.attach(self.spin_bg_b, 1, 8, 1, 1)

        label_bg_a = Gtk.Label(label=str_label_bg_a)
        label_bg_a.set_alignment(1, 0)
        grid_colors.attach(label_bg_a, 0, 9, 1, 1)

        adj_bg_a = Gtk.Adjustment(
                0.0,
                0.0,
                100.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_bg_a = Gtk.SpinButton(adjustment=adj_bg_a, hexpand=True)
        self.spin_bg_a.set_numeric(True)
        self.spin_bg_a.set_tooltip_text(str_tooltip_bg_a)
        grid_colors.attach(self.spin_bg_a, 1, 9, 1, 1)

        # add the grid to the stack with a name and a title
        stack.add_titled(grid_colors, "colors", str_tab_colors)

        # the third tab

        # create a grid with inter-spacig
        grid_sizes = Gtk.Grid()
        grid_sizes.set_row_spacing(20)
        grid_sizes.set_column_spacing(20)

        # create all the labels and spins with adjustments and numeric only
        label_width = Gtk.Label(label=str_label_width)
        label_width.set_alignment(1, 0)
        grid_sizes.attach(label_width, 0, 0, 1, 1)

        adj_width = Gtk.Adjustment(
                0.0,
                0.0,
                1000.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_width = Gtk.SpinButton(adjustment=adj_width, hexpand=True)
        self.spin_width.set_numeric(True)
        self.spin_width.set_tooltip_text(str_tooltip_width)
        grid_sizes.attach(self.spin_width, 1, 0, 1, 1)

        label_font_size = Gtk.Label(label=str_label_font_size)
        label_font_size.set_alignment(1, 0)
        grid_sizes.attach(label_font_size, 0, 1, 1, 1)

        adj_font_size = Gtk.Adjustment(
                0.0,
                0.0,
                50.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_font_size = Gtk.SpinButton(adjustment=adj_font_size,
                hexpand=True)
        self.spin_font_size.set_numeric(True)
        self.spin_font_size.set_tooltip_text(str_tooltip_font_size)
        grid_sizes.attach(self.spin_font_size, 1, 1, 1, 1)

        label_corner = Gtk.Label(label=str_label_corner)
        label_corner.set_alignment(1, 0)
        grid_sizes.attach(label_corner, 0, 2, 1, 1)

        adj_corner = Gtk.Adjustment(
                0.0,
                0.0,
                50.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_corner = Gtk.SpinButton(adjustment=adj_corner, hexpand=True)
        self.spin_corner.set_numeric(True)
        self.spin_corner.set_tooltip_text(str_tooltip_corner)
        grid_sizes.attach(self.spin_corner, 1, 2, 1, 1)

        label_border = Gtk.Label(label=str_label_border)
        label_border.set_alignment(1, 0)
        grid_sizes.attach(label_border, 0, 3, 1, 1)

        adj_border = Gtk.Adjustment(
                0.0,
                0.0,
                50.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_border = Gtk.SpinButton(adjustment=adj_border, hexpand=True)
        self.spin_border.set_numeric(True)
        self.spin_border.set_tooltip_text(str_tooltip_border)
        grid_sizes.attach(self.spin_border, 1, 3, 1, 1)

        label_top_pad = Gtk.Label(label=str_label_top_pad)
        label_top_pad.set_alignment(1, 0)
        grid_sizes.attach(label_top_pad, 0, 4, 1, 1)

        adj_top_pad = Gtk.Adjustment(
                0.0,
                0.0,
                100.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_top_pad = Gtk.SpinButton(adjustment=adj_top_pad, hexpand=True)
        self.spin_top_pad.set_numeric(True)
        self.spin_top_pad.set_tooltip_text(str_tooltip_top_pad)
        grid_sizes.attach(self.spin_top_pad, 1, 4, 1, 1)

        label_bottom_pad = Gtk.Label(label=str_label_bottom_pad)
        label_bottom_pad.set_alignment(1, 0)
        grid_sizes.attach(label_bottom_pad, 0, 5, 1, 1)

        adj_bottom_pad = Gtk.Adjustment(
                0.0,
                0.0,
                100.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_bottom_pad = Gtk.SpinButton(adjustment=adj_bottom_pad,
                hexpand=True)
        self.spin_bottom_pad.set_numeric(True)
        self.spin_bottom_pad.set_tooltip_text(str_tooltip_bottom_pad)
        grid_sizes.attach(self.spin_bottom_pad, 1, 5, 1, 1)

        label_side_pad = Gtk.Label(label=str_label_side_pad)
        label_side_pad.set_alignment(1, 0)
        grid_sizes.attach(label_side_pad, 0, 6, 1, 1)

        adj_side_pad = Gtk.Adjustment(
                0.0,
                0.0,
                100.0,
                1.0,
                5.0,
                0.0
        )
        self.spin_side_pad = Gtk.SpinButton(adjustment=adj_side_pad,
                hexpand=True)
        self.spin_side_pad.set_numeric(True)
        self.spin_side_pad.set_tooltip_text(str_tooltip_side_pad)
        grid_sizes.attach(self.spin_side_pad, 1, 6, 1, 1)

        # add the grid to the stack with a name and a title
        stack.add_titled(grid_sizes, "sizes", str_tab_sizes)

        # create a box for the buttons
        hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                spacing=20)

        # create the buttons
        button_ok = Gtk.Button(label=str_button_ok)
        button_ok.connect("clicked", self.button_ok_clicked)
        hbox_buttons.pack_start(button_ok, True, True, 0)

        button_cancel = Gtk.Button(label=str_button_cancel)
        button_cancel.connect("clicked", self.button_cancel_clicked)
        hbox_buttons.pack_start(button_cancel, True, True, 0)

        button_apply = Gtk.Button(label=str_button_apply)
        button_apply.connect("clicked", self.button_apply_clicked)
        hbox_buttons.pack_start(button_apply, True, True, 0)

        # create a vbox for the switcher box, stack, and button box and add it
        # as main window's content
        vbox_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=50)
        self.add(vbox_content)

        # add the switcher's box, the stack, and button box as content
        # do not resize switcher's box (horizontal fill is implicit)
        # fully resize stack
        # do not resize button box either
        vbox_content.pack_start(hbox_switcher, False, False, 0)
        vbox_content.pack_start(stack, True, True, 0)
        vbox_content.pack_start(hbox_buttons, False, False, 0)

        # load props or defaults
        self.load_config()

        # do switch routines
        self.switch_caption_clicked(self.switch_caption, 0)
        self.switch_enabled_clicked(self.switch_enabled, 0)

    # load values from config file
    def load_config(self):

        # set defaults
        self.switch_enabled.set_active(int(def_enabled))
        self.spin_delay.set_value(int(def_delay))
        self.switch_caption.set_active(int(def_caption))

        self.spin_text_r.set_value(int(def_text_r))
        self.spin_text_g.set_value(int(def_text_g))
        self.spin_text_b.set_value(int(def_text_b))
        self.spin_text_a.set_value(int(def_text_a))
        self.spin_bg_r.set_value(int(def_bg_r))
        self.spin_bg_g.set_value(int(def_bg_g))
        self.spin_bg_b.set_value(int(def_bg_b))
        self.spin_bg_a.set_value(int(def_bg_a))

        for short_pos, long_pos in position_map.items():
            if def_position == short_pos:
                self.combo_position.set_active_id(short_pos)
        self.spin_width.set_value(int(def_width))
        self.spin_font_size.set_value(int(def_font_size))
        self.spin_corner.set_value(int(def_corner))
        self.spin_border.set_value(int(def_border))
        self.spin_top_pad.set_value(int(def_top_pad))
        self.spin_bottom_pad.set_value(int(def_bottom_pad))
        self.spin_side_pad.set_value(int(def_side_pad))

        # check if config file exists
        if os.path.exists(conf_file):

            # open config file and get all lines
            with open(conf_file, "r") as f:
                lines = f.readlines()

                # try to find a value in the conf file
                for line in lines:
                    line_clean = line.strip().upper()

                    # ignore comment lines
                    if line_clean.startswith("#") or line_clean == "":
                        continue

                    # split key off at equals
                    key_val = line_clean.split("=")
                    key = key_val[0].strip()

                    # split val off ignoring trailing comments
                    val = ""
                    if (len(key_val) > 1):
                        val_array = key_val[1].split("#")
                        val = val_array[0].strip()

                    # set values for keys

                    if key == "ENABLED":
                        if val != "":
                            self.switch_enabled.set_active(int(val))
                    if key == "DELAY":
                        if val != "":
                            self.spin_delay.set_value(int(val))
                    if key == "CAPTION":
                        if val != "":
                            self.switch_caption.set_active(int(val))
                    if key == "POSITION":
                        for short_pos, long_pos in position_map.items():
                            if val == short_pos:
                                self.combo_position.set_active_id(short_pos)

                    if key == "TEXT_R":
                        if val != "":
                            self.spin_text_r.set_value(int(val))
                    if key == "TEXT_G":
                        if val != "":
                            self.spin_text_g.set_value(int(val))
                    if key == "TEXT_B":
                        if val != "":
                            self.spin_text_b.set_value(int(val))
                    if key == "TEXT_A":
                        if val != "":
                            self.spin_text_a.set_value(int(val))
                    if key == "BG_R":
                        if val != "":
                            self.spin_bg_r.set_value(int(val))
                    if key == "BG_G":
                        if val != "":
                            self.spin_bg_g.set_value(int(val))
                    if key == "BG_B" in key:
                        if val != "":
                            self.spin_bg_b.set_value(int(val))
                    if key == "BG_A":
                        if val != "":
                            self.spin_bg_a.set_value(int(val))

                    if key == "WIDTH":
                        if val != "":
                            self.spin_width.set_value(int(val))
                    if key == "FONT_SIZE":
                        if val != "":
                            self.spin_font_size.set_value(int(val))
                    if key == "CORNER_RADIUS":
                        if val != "":
                            self.spin_corner.set_value(int(val))
                    if key == "BORDER":
                        if val != "":
                            self.spin_border.set_value(int(val))
                    if key == "TOP_PADDING":
                        if val != "":
                            if val != "":
                                self.spin_top_pad.set_value(int(val))
                    if key == "BOTTOM_PADDING":
                        if val != "":
                            self.spin_bottom_pad.set_value(int(val))
                    if key == "SIDE_PADDING":
                        if val != "":
                            self.spin_side_pad.set_value(int(val))

    def save_config(self):

        # open or create config file
        with open(conf_file, "w+") as f:

            # TODO: find line for key, replace value instead of overwriting
            # whole file

            f.write("# DO NOT EDIT THIS FILE BY HAND!\n\n")

            # start writing options
            f.write("ENABLED=" + str(int(self.switch_enabled.get_active())) +
                    "\n")
            f.write("DELAY=" + str(int(self.spin_delay.get_value())) + "\n")
            f.write("CAPTION=" + str(int(self.switch_caption.get_active())) +
                    "\n")
                    
            # fudge the position option from the array
            val = self.combo_position.get_active_text()
            for short_pos, long_pos in position_map.items():
                if val == long_pos:
                    f.write("POSITION=" + short_pos + "\n")
                    break

            f.write("TEXT_R=" + str(int(self.spin_text_r.get_value())) + "\n")
            f.write("TEXT_G=" + str(int(self.spin_text_g.get_value())) + "\n")
            f.write("TEXT_B=" + str(int(self.spin_text_b.get_value())) + "\n")
            f.write("TEXT_A=" + str(int(self.spin_text_a.get_value())) + "\n")
            f.write("BG_R=" + str(int(self.spin_bg_r.get_value())) + "\n")
            f.write("BG_G=" + str(int(self.spin_bg_g.get_value())) + "\n")
            f.write("BG_B=" + str(int(self.spin_bg_b.get_value())) + "\n")
            f.write("BG_A=" + str(int(self.spin_bg_a.get_value())) + "\n")


            f.write("WIDTH=" + str(int(self.spin_width.get_value())) + "\n")
            f.write("FONT_SIZE=" + str(int(self.spin_font_size.get_value())) +
                    "\n")
            f.write("CORNER_RADIUS=" + str(int(self.spin_corner.get_value())) +
                    "\n")
            f.write("BORDER=" + str(int(self.spin_border.get_value())) + "\n")
            f.write("TOP_PADDING=" + str(int(self.spin_top_pad.get_value())) +
                    "\n")
            f.write("BOTTOM_PADDING=" +
                    str(int(self.spin_bottom_pad.get_value())) + "\n")
            f.write("SIDE_PADDING=" + str(int(self.spin_side_pad.get_value())) +
                    "\n")

    def run_prog(self):

        logging.debug('GUI')

        # only run once, no listener
        cmd_array = run_prog_cmd.split()

        # non-blocking subprocess
        subprocess.Popen(cmd_array)

    def switch_enabled_clicked(self, widget, gparam):
        if widget.get_active():
            self.spin_delay.set_sensitive(True)
            self.switch_caption.set_sensitive(True)
            self.switch_caption_clicked(self.switch_caption, 0)
        else:
            self.spin_delay.set_sensitive(False)
            self.switch_caption.set_sensitive(False)

            self.spin_text_r.set_sensitive(False)
            self.spin_text_g.set_sensitive(False)
            self.spin_text_b.set_sensitive(False)
            self.spin_text_a.set_sensitive(False)
            self.spin_bg_r.set_sensitive(False)
            self.spin_bg_g.set_sensitive(False)
            self.spin_bg_b.set_sensitive(False)
            self.spin_bg_a.set_sensitive(False)

            self.combo_position.set_sensitive(False)
            self.spin_width.set_sensitive(False)
            self.spin_font_size.set_sensitive(False)
            self.spin_corner.set_sensitive(False)
            self.spin_border.set_sensitive(False)
            self.spin_top_pad.set_sensitive(False)
            self.spin_bottom_pad.set_sensitive(False)
            self.spin_side_pad.set_sensitive(False)

    def switch_caption_clicked(self, widget, gparam):
        if widget.get_active():
            self.spin_text_r.set_sensitive(True)
            self.spin_text_g.set_sensitive(True)
            self.spin_text_b.set_sensitive(True)
            self.spin_text_a.set_sensitive(True)
            self.spin_bg_r.set_sensitive(True)
            self.spin_bg_g.set_sensitive(True)
            self.spin_bg_b.set_sensitive(True)
            self.spin_bg_a.set_sensitive(True)

            self.combo_position.set_sensitive(True)
            self.spin_width.set_sensitive(True)
            self.spin_font_size.set_sensitive(True)
            self.spin_corner.set_sensitive(True)
            self.spin_border.set_sensitive(True)
            self.spin_top_pad.set_sensitive(True)
            self.spin_bottom_pad.set_sensitive(True)
            self.spin_side_pad.set_sensitive(True)
        else:
            self.spin_text_r.set_sensitive(False)
            self.spin_text_g.set_sensitive(False)
            self.spin_text_b.set_sensitive(False)
            self.spin_text_a.set_sensitive(False)
            self.spin_bg_r.set_sensitive(False)
            self.spin_bg_g.set_sensitive(False)
            self.spin_bg_b.set_sensitive(False)
            self.spin_bg_a.set_sensitive(False)

            self.combo_position.set_sensitive(False)
            self.spin_width.set_sensitive(False)
            self.spin_font_size.set_sensitive(False)
            self.spin_corner.set_sensitive(False)
            self.spin_border.set_sensitive(False)
            self.spin_top_pad.set_sensitive(False)
            self.spin_bottom_pad.set_sensitive(False)
            self.spin_side_pad.set_sensitive(False)

    def button_ok_clicked(self, widget):
        self.save_config()
        self.run_prog()
        self.destroy()

    def button_cancel_clicked(self, widget):
        self.destroy()

    def button_apply_clicked(self, widget):
        self.save_config()
        self.run_prog()

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()

Gtk.main()

# -)

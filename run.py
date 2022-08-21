#!/usr/bin/env python3

import os

prog_name = 'spaceoddity'
home_dir = os.path.expanduser('~')
src_dir = os.path.dirname(os.path.realpath(__file__))
app_dir = os.path.join(f'{home_dir}/.{prog_name}')

app_files = {
    f'{prog_name}_main.py',
    f'{prog_name}_caption.py',
    f'gui/{prog_name}_gui.py',
    f'gui/{prog_name}.glade',
    'static/VERSION.txt'
}

if not os.path.exists(app_dir):
    os.makedirs(app_dir)

for file in app_files:

    src_path = os.path.join(src_dir, file)
    dst_path = os.path.join(app_dir, file)

    dst_dir = os.path.dirname(dst_path)
    print(dst_dir)
    # if not os.path.exists(dst_dir):
    #     os.makedirs(dst_dir)

    # os.system(f'cp {src_path} {dst_dir}')

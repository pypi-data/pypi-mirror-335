"""
Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>

SPDX-License-Identifier: MIT
"""
import os
import subprocess

RES_16 = '16'
RES_32 = '32'
RES_64 = '64'
RES_128 = '128'
RES_256 = '256'
RES_512 = '512'
RES_1024 = '1024'

ICONSET_FILE = 'icon.iconset'
ICNS_FILE = 'icon.isnc'

def icon_filename(res, doubled):
    return f'icon_{res}x{res}{"" if not doubled else "@2x"}.png'

PNG_RES_FILES = [
    {
        'res': RES_32,
        'filename': icon_filename(RES_16, doubled=True),
    },
    {
        'res': RES_32,
        'filename': icon_filename(RES_32, doubled=False),
    },
    {
        'res': RES_64,
        'filename': icon_filename(RES_64, doubled=False),
    },
    {
        'res': RES_128,
        'filename': icon_filename(RES_64, doubled=True),
    },
    {
        'res': RES_256,
        'filename': icon_filename(RES_128, doubled=True),
    },
    {
        'res': RES_256,
        'filename': icon_filename(RES_256, doubled=False),
    },
    {
        'res': RES_512,
        'filename': icon_filename(RES_256, doubled=True),
    },
    {
        'res': RES_1024,
        'filename': icon_filename(RES_512, doubled=True),
    },
]

def main():
    if not os.path.exists(ICONSET_FILE):
        os.mkdir(ICONSET_FILE)
    for file_gen in PNG_RES_FILES:
        subprocess.check_call([
            'rsvg-convert',
            '-h',
            file_gen['res'],
            'iprm_icon.svg',
            '-o',
            f'{ICONSET_FILE}/{file_gen["filename"]}',
        ])
    subprocess.check_call([
        'iconutil',
        '-c',
        'icns',
        ICONSET_FILE,
    ])


if __name__ == "__main__":
    main()

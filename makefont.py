#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014, Ryan Dorsey (ryanjdorsey at gmail dot com),
# with Reserved Font Name Mazon (מזון).
#
# This Font Software is licensed under the SIL Open Font License, Version 1.1.
# This license is copied below, and is also available with a FAQ at:
# http://scripts.sil.org/OFL

from __future__ import division, print_function
import argparse
import os
import os.path as path
import subprocess as sub
import sys
import unicodedata

import fontforge
import psMat

if sys.version_info.major < 3:
    input = raw_input

config = None

def download_local_toml():
    TOMLVER = '0.8.2'

    if os.path.exists('toml-' + TOMLVER) or os.path.exists('toml.py'):
        printerr('Exiting, since toml files already exist in the current '
                 'directory')
        sys.exit(1)

    try:
        if sys.platform.startswith('win32'):
            raise Exception('Windows support not yet included.  Sorry!')
        else:
            wget = sub.Popen(['wget', '-O', '-',
                              'https://pypi.python.org/packages/source/t/toml/toml-' + TOMLVER + '.tar.gz'],
                             stdout=sub.PIPE)
            sub.check_call(['tar', '-xz'], stdin=wget.stdout)
            wget.wait()
            sub.check_call(['mv', 'toml-' + TOMLVER + '/toml.py', 'toml.py'])
            sub.check_call(['rm', '-r', 'toml-' + TOMLVER])
    except Exception as e:
        printerr('Local toml install failed: {}'.format(e))
        sys.exit(1)

# Unfortunately, this can only be done with a font that is *already* available.
# So if you need to use it, run generate, then find the em width, then generate,
# etc.
def find_em_width():
    font = fontforge.open('MazonHebrew-Regular.sfd')
    total = 0
    for c in config['em width chars']:
        total += font[ord(c)].width
    font.close()
    return float(total) / len(config['em width chars'])

def generate():
    font = fontforge.font()
    # Some basic metadata.
    font.copyright   = ('Copyright (c) 2014 Ryan Dorsey\n'
                        'Licensed under SIL Open Font License v1.1 '
                        '(http://scripts.sil.org/OFL)\n'
                        'Created with FontForge 2.0 (http://fontforge.sf.net)')
    font.encoding    = config['specs']['encoding']
    font.descent     = config['specs']['descent']
    font.ascent      = config['specs']['ascent']
    font.familyname  = config['specs']['family name']
    font.fontname    = config['specs']['font name']
    font.fullname    = config['specs']['full name']
    font.version     = config['specs']['version']
    font.weight      = config['specs']['weight']

    # This works, but prints out "failed to parse color" 6 times per glyph.
    # That is going to be annoying as heck unless I can suppress that output.
    for d in config['directories'].values():
        for f in os.listdir(d):
            fullpath = path.join(d, f)
            if path.isfile(fullpath):
                print('Processing file: {}'.format(f))
                # Retrieve the filename sans extension, i.e., the glyph's
                # unicode name.
                glyphname = path.splitext(path.basename(f))[0]
                try:
                    glyphnum = ord(unicodedata.lookup(glyphname))
                except KeyError:
                    printerr(('Filename `{}` does not correspond to a '
                              'unicode name').format(fullpath),
                             level='Warning')
                    continue
                glyph = font.createChar(glyphnum)
                glyph.importOutlines(fullpath)
                glyph.correctDirection()
                glyph.left_side_bearing  = 60
                glyph.right_side_bearing = 60

    # Make whitespace characters.
    for (spacechar, spacewidth) in config['specs']['spaces'].items():
        print('Creating space: {}'.format(spacechar))
        try:
            glyphnum = ord(unicodedata.lookup(spacechar))
        except KeyError:
            printerr('`{}` in SPACES does not correspond to a unicode name'
                     .format(spacechar), level='Warning')
            continue
        glyph = font.createChar(glyphnum)
        glyph.width = int(round(spacewidth * config['specs']['real em']))

    font.save('MazonHebrew-Regular.gen.sfd')
    font.generate('MazonHebrew-Regular.gen.otf')

def printerr(errmsg, level='Error'):
    red = '\033[31;1m'
    reset = '\033[0m'
    print(red + level + ': ' + errmsg + reset, file=sys.stderr)

if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-m', '--find-em-width',
                           help='find the actual em width of the font',
                           action='store_true')
    argparser.add_argument('--install-local-package',
                           help='install a python package to the current directory',
                           action='append',
                           dest='packages')
    args = argparser.parse_args()

    if args.packages:
        # Currently we only need one non-standard package, but in the future
        # maybe there will be more?
        download_local_toml()

    try:
        import toml
        config = toml.load('config.toml')
        # TODO: get this to import properly as unicode from config.toml
        #
        # These are the "standard-width" characters in Hebrew.  The rest are
        # much narrower, excepting shin, which is a bit wider.
        config['em width chars'] = u'אבדהחטכךלמםסעפףצקרת'
    except ImportError:
        print('''\
You do not have the python module `toml` installed. This is required to read
the configuration file which describes our font.  To install this package,
you have three options:
    1) Run `[sudo] pip install toml`.
    2) Manually install the toml package.  Maybe your OS's package manager can
       do this for you, or you can download it from
       http://pypi.python.org/pypi/toml/0.8.2 or https://github.com/uiri/toml/
    3) Try to install a copy into this directory by running
       `makefont.py --install-local-package toml`''')
        sys.exit(1)

    if len(sys.argv) == 1:
        generate()
    else:
        if args.find_em_width:
            print('The average em-width is: {}'.format(find_em_width()))

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

config = None

try:
    import toml
except ImportError:
    print('''\
You do not have the package `toml` installed.  You can install it from
    github.com/uiri/toml
After installation, rerun this tool.''')
    sys.exit(1)


if sys.version_info.major < 3:
    input = raw_input
else:
    unichr = chr

high_niqqud_glyphnames = [ 'hebrew point holam',
                           'hebrew point holam haser for vav',
                           'hebrew point shin dot',
                           'hebrew point sin dot',
                         ]
# These are the "standard-width" characters in Hebrew.  The rest are
# much narrower, excepting shin, which is a bit wider.
em_width_chars = u'אבדהחטכךלמםסעפףצקרת'

# Unfortunately, this can only be done with a font that is *already* available.
# So if you need to use it, run generate, then find the em width, then generate,
# etc.
def find_em_width():
    font = fontforge.open('MazonHebrew-Regular.sfd')
    total = 0
    for c in em_width_chars:
        total += font[ord(c)].width
    font.close()
    return float(total) / len(em_width_chars)

def generate():
    font = fontforge.font()
    # Some basic metadata.
    font.copyright   = ('Copyright (c) 2014 Ryan Dorsey\n'
                        'Licensed under SIL Open Font License v1.1 '
                        '(http://scripts.sil.org/OFL)\n'
                        'Created with FontForge 2.0 (http://fontforge.sf.net)')
    font.encoding    = config['specs']['encoding']
    font.em          = config['specs']['fontforge em']
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
            # This avoids accidentally processing subdirectories.  If I ever
            # want to change the directory structure drastically, then I can
            # investigate os.walk().
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

                # TODO: This needs to be cleaned up.
                # Adjust the bearings of the glyph.  Niqqudot need a zero width.
                # Most have equal bearings, but the high niqqudot are designed
                # to be offset.  It makes setting the anchors simpler.
                #
                # Also, add anchor points.
                if d == './Draft Material/Niqqudot':
                    glyph.width = 0
                    bounds = glyph.boundingBox()
                    if glyphname in high_niqqud_glyphnames:
                        # HighNiqqud glyphs need to keep their bearings.
                        # The 100 comes from the guides set up in the .svgs.
                        glyph.left_side_bearing -= 100
                        glyph.right_side_bearing += 100
                    else:
                        # TODO: This leaves the width of the glyph as 1.
                        #       Setting it to zero again will make it
                        #       zero, but off center slightly.  How to
                        #       fix this?
                        orig_width = bounds[2] - bounds[0]
                        bearing = orig_width / 2.0
                        glyph.left_side_bearing = -bearing
                        glyph.right_side_bearing = -bearing

                elif d == './Draft Material/Letterforms':
                    glyph.left_side_bearing  = 60
                    glyph.right_side_bearing = 60
                else:
                    glyph.left_side_bearing  = 60
                    glyph.right_side_bearing = 60

    # Make Private Use Area chars
    glyph = font.createChar(0xf300, 'afii57668.fp')
    glyph.addReference('afii57668')
    glyph.useRefsMetrics('afii57668')

    glyph = font.createChar(0xf301, 'afii57671.fp')
    glyph.addReference('afii57671')
    glyph.useRefsMetrics('afii57671')

    glyph = font.createChar(0xf302, 'afii57682.fp')
    glyph.addReference('afii57682')
    glyph.useRefsMetrics('afii57682')

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

    font.mergeFeature('MazonHebrew-Regular.fea')
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
    args = argparser.parse_args()

    with open('config.toml') as conffile:
        config = toml.loads(conffile.read())

    if len(sys.argv) == 1:
        generate()
    else:
        if args.find_em_width:
            print('The average em-width is: {}'.format(find_em_width()))

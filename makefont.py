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
else:
    unichr = chr

# This gets loaded from config.toml below, in main, to allow the program to
# run --install-local-package
config = None

def correct_anchors(glyph):
    currents = glyph.anchorPoints
    try:
        corrections = config[unicodedata.name(unichr(glyph.unicode))
                             .lower()]['corrections']
    except KeyError:
        return

    # Don't tuple unpack in the for statement.  If there are ever
    # ligatures, the four-tuple destructure will fail.
    for anchor in currents:
        (anchor_name, typ, x, y) = anchor[0:4]
        if typ != 'base':
            continue
        else:
            try:
                (x, y) = corrections[anchor_name]
            except KeyError:
                pass
            glyph.addAnchorPoint(anchor_name, typ, x, y)

# The fourth argument to addLookup is called the `feature-script-lang-tuple`
# in fontforge's python documentation.  It's a five deep tuple, whose structure
# looks like this (each ___ in the tuples represents an entry from config.toml
# whose schema is given to the right of the tuple:
#
#     ( ___, ... ) lookups.features
#       /
#       `> ("lookups.features.name", ( ___, ... )) lookups.features.scripts
#                                       |
#                                       v
#                      ( "lookups.features.scripts.name",
#                        ("lookups.features.scripts.langs", ...))
#
# It goes without saying, be careful when messing with that tuple
# generator below!
def create_lookups(font):
    for lookup in config['lookups']:
        font.addLookup(lookup['name'],
                       lookup['type'],
                       lookup['flags'],
                       tuple( (feature['name'],                           \
                               tuple( (script['name'],                    \
                                       tuple(l for l in script['langs'])) \
                                    for script in feature['scripts'] ))   \
                            for feature in lookup['features'] )
                      )

        # This may not be strictly correct, but for the limited number and
        # types of sublookups I'm dealing with, it currently suffices.
        for sub in lookup['subtables']:
            font.addLookupSubtable(lookup['name'], sub['name'])
            if lookup['type'] == 'gpos_mark2base':
                font.addAnchorClass(sub['name'], sub['mark name'])

def download_local_toml():
    if os.path.exists('toml-master/') or os.path.exists('toml.py'):
        printerr('Exiting, since toml files already exist in the current '
                 'directory')
        sys.exit(1)

    try:
        if sys.platform.startswith('win32'):
            raise Exception('Windows support not yet included.  Sorry!')
        else:
            wget = sub.Popen(['wget', '-O', '-',
                              ('https://github.com/uiri/toml/'
                               'archive/master.zip')],
                             stdout=sub.PIPE)
            sub.check_call(['unzip'], stdin=wget.stdout)
            wget.wait()
            sub.check_call(['mv', 'toml-master/toml.py', 'toml.py'])
            sub.check_call(['rm', '-r', 'toml-master/'])
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
    font.em          = config['specs']['fontforge em']
    font.descent     = config['specs']['descent']
    font.ascent      = config['specs']['ascent']
    font.familyname  = config['specs']['family name']
    font.fontname    = config['specs']['font name']
    font.fullname    = config['specs']['full name']
    font.version     = config['specs']['version']
    font.weight      = config['specs']['weight']

    create_lookups(font)

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
                if is_glyph_type(glyph, 'niqqud'):
                    glyph.width = 0
                    bounds = glyph.boundingBox()
                    if glyphname in config['anchors']['HighNiqqud']['glyphs']:
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

                    for (anchorname, glyphlist) in config['anchors'].items():
                        if glyphname in glyphlist['glyphs']:
                            glyph.addAnchorPoint(anchorname, 'mark', 0, 0)
                elif is_glyph_type(glyph, 'punctuation'):
                    glyph.left_side_bearing  = 60
                    glyph.right_side_bearing = 60
                elif is_glyph_type(glyph, 'letter'):
                    glyph.left_side_bearing  = 60
                    glyph.right_side_bearing = 60
                    bounds = glyph.boundingBox()
                    glyph.addAnchorPoint('LowNarrowNiqqud', 'base',
                                         glyph.width / 2.0, 0)
                    glyph.addAnchorPoint('LowWideNiqqud', 'base',
                                         glyph.width / 2.0, 0)
                    glyph.addAnchorPoint('Dagesh', 'base',
                                         glyph.width / 2.0, 0)
                    glyph.addAnchorPoint('Rafe', 'base',
                                         glyph.width / 2.0, 0)
                    glyph.addAnchorPoint('HighNiqqud', 'base',
                                         bounds[0], 0)
                    correct_anchors(glyph)

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

# typ is a tuple containing groups to search for the union of.
def is_glyph_type(glyph, typ):
    if isinstance(glyph, fontforge.glyph):
        point = glyph.unicode
    elif isinstance(glyph, str):
        point = ord(unicodedata.lookup(glyph))
    elif isinstance(glyph, int):
        point = glyph
    else:
        raise ValueError('Not an appropriate argument to `is_glyph_type()`.')

    typechecks = {'letter': (lambda pt:
                             unicodedata.category(unichr(pt))[0] == 'L'),
                  'niqqud': (lambda pt:
                             pt in (set(range(0x05b0, 0x5bd + 1))
                                    | set((0x05bf, 0x05c1, 0x05c2, 0x05c7)))),
                  'punctuation': (lambda pt:
                                  unicodedata.category(unichr(pt))[0] == 'P'),
                  'space': (lambda pt:
                            unicodedata.category(unichr(pt))[0] == 'Z'),
                  'wide': (lambda pt:
                           pt in (set(range(0x05b1, 0x05b3 + 1))))}
    return typechecks[typ](point)

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
        with open('config.toml') as conffile:
            config = toml.loads(conffile.read())
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

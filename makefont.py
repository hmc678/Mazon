#!/usr/bin/env fontforge
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014, Ryan Dorsey (ryanjdorsey at gmail dot com),
# with Reserved Font Name Mazon (מזון).
#
# This Font Software is licensed under the SIL Open Font License, Version 1.1.
# This license is copied below, and is also available with a FAQ at:
# http://scripts.sil.org/OFL

import fontforge, psMat
import unicodedata
import os
import os.path as path

# Colors for printing
TERMCOLORRED = '\033[31;1m'
TERMRESET = '\033[0m'

# A listing of directories in which makefont should search for glyphs.
DIRS = ('./Draft Material/Letterforms',
        './Draft Material/Punctuation',
)
# The whitespace characters to generate, and their dimensions, in ems.
# These are in order, by unicode point.  Let's keep 'em that way for
# convenience.
EMWIDTH = 650
SPACES = (('space',                 0.4),
          ('no-break space',        0.4),
          ('en quad',               0.5),
          ('em quad',               1.0),
          ('en space',              0.5),
          ('em space',              1.0),
          ('thin space',            0.2),
          ('hair space',            0.1),
          ('zero width space',      0.0),
          # Not a space, but might as well go here
          ('right-to-left mark',    0.0),
)

font = fontforge.font()
# Some basic metadata.
font.encoding    = 'UnicodeBmp'
font.copyright   = ('Copyright (c) 2014 Ryan Dorsey\n'
                    'Licensed under SIL Open Font License v1.1 (http://scripts.sil.org/OFL)\n'
                    'Created with FontForge 2.0 (http://fontforge.sf.net)')
font.familyname  = 'Mazon Hebrew'
font.fontname    = 'MazonHebrew-Regular'
font.fullname    = 'Mazon Hebrew Regular'
font.version     = 'v0.1'
font.weight      = 'Regular'
font.descent     = 247.0
font.ascent      = 1000.0 - 247.0

# This works, but prints out "failed to parse color" 6 times per glyph.
# That is going to be annoying as heck unless I can suppress that output.
#
# TODO: Needs to handle `space` specially.
for d in DIRS:
    for f in os.listdir(d):
        fullpath = path.join(d, f)
        if path.isfile(fullpath):
            print 'Processing file: {}'.format(f)
            # Retrieve the filename sans extension, i.e., the glyph's unicode
            # name.
            glyphname = path.splitext(path.basename(f))[0]
            try:
                glyphnum = ord(unicodedata.lookup(glyphname))
            except KeyError:
                print (TERMCOLORRED
                       + 'Filename `{}` does not correspond to a unicode name'
                       + TERMRESET).format(fullpath)
                continue
            glyph = font.createChar(glyphnum)
            glyph.importOutlines(fullpath)
            glyph.correctDirection()
            glyph.left_side_bearing  = 60
            glyph.right_side_bearing = 60

# Make whitespace characters.
for (spacechar, spacewidth) in SPACES:
    print 'Creating space: {}'.format(spacechar)
    try:
        glyphnum = ord(unicodedata.lookup(spacechar))
    except KeyError:
        print (TERMCOLORRED
               + '`{}` in SPACES does not correspond to a unicode name'
               + TERMRESET).format(spacechar)
    glyph = font.createChar(glyphnum)
    glyph.width = int(round(spacewidth * EMWIDTH))
    

font.save('MazonHebrew-Regular.gen.sfd')
font.generate('MazonHebrew-Regular.gen.otf')

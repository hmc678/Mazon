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
import os, sys
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
          ('three-per-em space',    0.3333),
          ('four-per-em space',     0.25),
          ('six-per-em space',      0.1667),
          # ('figure space', )
          # ('punctuation space', )
          ('thin space',            0.2),
          ('hair space',            0.1),
          ('zero width space',      0.0),
          ('zero width non-joiner', 0.0),
          ('zero width joiner',     0.0),
          # Not spaces, but might as well go here
          ('left-to-right mark',    0.0),
          ('right-to-left mark',    0.0),
)

# Unfortunately, this can only be done with a font that is *already* available.
# So if you need to use it, run generate, then find the em width, then generate,
# etc.
def find_em_width():
    font = fontforge.open('MazonHebrew-Regular.sfd')
    # These are the "standard-width" characters in Hebrew.  The rest are
    # much narrower, excepting shin, which is a bit wider.
    em_width_chars = u'אבדהחטכךלמםסעפףצקרת'
    total = 0
    for c in em_width_chars:
        total += font[ord(c)].width
    font.close()
    return float(total) / len(em_width_chars)

def generate():
    font = fontforge.font()
    # Some basic metadata.
    font.copyright   = ('Copyright (c) 2014 Ryan Dorsey\n'
                        'Licensed under SIL Open Font License v1.1 (http://scripts.sil.org/OFL)\n'
                        'Created with FontForge 2.0 (http://fontforge.sf.net)')
    font.encoding    = 'UnicodeBmp'
    font.descent     = 247.0
    font.ascent      = 1000.0 - font.descent # calculate after font.descent
    font.familyname  = 'Mazon Hebrew'
    font.fontname    = 'MazonHebrew-Regular'
    font.fullname    = 'Mazon Hebrew Regular'
    font.version     = 'v0.1'
    font.weight      = 'Regular'

    # This works, but prints out "failed to parse color" 6 times per glyph.
    # That is going to be annoying as heck unless I can suppress that output.
    #
    # TODO: Needs to handle `space` specially.
    for d in DIRS:
        for f in os.listdir(d):
            fullpath = path.join(d, f)
            if path.isfile(fullpath):
                print 'Processing file: {}'.format(f)
                # Retrieve the filename sans extension, i.e., the glyph's
                # unicode name.
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
            continue
        glyph = font.createChar(glyphnum)
        glyph.width = int(round(spacewidth * EMWIDTH))

    font.save('MazonHebrew-Regular.gen.sfd')
    font.generate('MazonHebrew-Regular.gen.otf')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        generate()

    else:
        if sys.argv[1] == '--find-em-width' or sys.argv[1] == '-m':
            print 'The average em-width is: ', find_em_width()

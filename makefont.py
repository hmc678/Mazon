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

# A listing of directories in which makefont should search for glyphs.
DIRS = ('./Draft Material/Letterforms',
        './Draft Material/Punctuation',
)

font = fontforge.font()
# Some basic metadata.
font.encoding   = 'UnicodeBmp'
font.copyright  = ('Copyright (c) 2014 Ryan Dorsey\n'
                   'Licensed under SIL Open Font License v1.1 (http://scripts.sil.org/OFL)\n'
                   'Created with FontForge 2.0 (http://fontforge.sf.net)')
font.familyname = 'Mazon Hebrew'
font.fontname   = 'MazonHebrew-Regular'
font.fullname   = 'Mazon Hebrew Regular'
font.version    = 'v0.1'
font.weight     = 'Regular'

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
                print ('\033[31;1mFilename `{}` does not correspond to a unicode'
                       'name\033[0m'.format(fullpath))
                continue
            glyph = font.createChar(glyphnum)
            glyph.importOutlines(fullpath)
            # This value is subject to change and seems to just be a capricious
            # side effect of the svg import.
            glyph.transform(psMat.translate(0, -50))
            glyph.left_side_bearing  = 60
            glyph.right_side_bearing = 60

font.save('MazonHebrew-Regular.gen.sfd')
font.generate('MazonHebrew-Regular.gen.otf')

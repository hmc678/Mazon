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

# TODO: make this less fatal and more helpful.  Maybe have a local version?
try:
    import toml
except ImportError:
    print 'Please install toml, perhaps via `pip install toml`?'
    exit(1)

config = toml.load('config.toml')

# Should these be in the config file?  I dunno....
config['term color red'] = '\033[31;1m'
config['term reset'] = '\033[0m'
# These are the "standard-width" characters in Hebrew.  The rest are
# much narrower, excepting shin, which is a bit wider.
config['em width chars'] = u'אבדהחטכךלמםסעפףצקרת'

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
                        'Licensed under SIL Open Font License v1.1 (http://scripts.sil.org/OFL)\n'
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
                print 'Processing file: {}'.format(f)
                # Retrieve the filename sans extension, i.e., the glyph's
                # unicode name.
                glyphname = path.splitext(path.basename(f))[0]
                try:
                    glyphnum = ord(unicodedata.lookup(glyphname))
                except KeyError:
                    print (config['term color red']
                           + 'Filename `{}` does not correspond to a unicode name'
                           + config['term reset']).format(fullpath)
                    continue
                glyph = font.createChar(glyphnum)
                glyph.importOutlines(fullpath)
                glyph.correctDirection()
                glyph.left_side_bearing  = 60
                glyph.right_side_bearing = 60

    # Make whitespace characters.
    for (spacechar, spacewidth) in config['specs']['spaces'].items():
        print 'Creating space: {}'.format(spacechar)
        try:
            glyphnum = ord(unicodedata.lookup(spacechar))
        except KeyError:
            print (config['term color red']
                   + '`{}` in SPACES does not correspond to a unicode name'
                   + config['term reset']).format(spacechar)
            continue
        glyph = font.createChar(glyphnum)
        glyph.width = int(round(spacewidth * config['specs']['real em']))

    font.save('MazonHebrew-Regular.gen.sfd')
    font.generate('MazonHebrew-Regular.gen.otf')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        generate()

    else:
        if sys.argv[1] == '--find-em-width' or sys.argv[1] == '-m':
            print 'The average em-width is: {}'.format(find_em_width())

# FONTLOG for Mazon

This file provides detailed information on the Mazon Font Software.  This information should be distributed along with the Mazon fonts and any derivative works.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
http://scripts.sil.org/OFL

# Detailed Information

## Design goals

Hebrew typefaces have a long and somewhat antagonistic relationship with Latin typefaces.  The two do not share a very common lineage in the same way that, perhaps, Cyrillic and Latin do, and thus have rather different "characters", if you will pardon the pun.  The two faces read in opposite directions.  And in particular, while Latin glyphs tend to emphasize their vertical strokes (which can be seen to a grotesque degree in the Romantic typefaces of Bodoni and Didot), Hebrew glyphs tend to emphasize their horizontal strokes (frequently to a similar degree of contrast as Romantic Latin typefaces).

The design goals of contemporary Hebrew font designers seem, to me (Ryan Dorsey), frequently orthogonal to, if not conflicting with, the goal of mixing well with Latin characters.  Many designs (found, e.g., in the Masterfont catalog) tend to have a rich rotundity that somehow doesn't match even the bowls of most romans, or a thickness that seems to be more aligned with other Afro-Semitic designs, rather than their northern cousin(s).  Also, the glyphs tend toward square (again, with emphasis on the horizontal motion) shapes, rather than the columnar rectangles of the roman.  Sans-serif fonts seem to escape these criticisms more frequently, but that leaves much to be desired when searching for a suitable type family for setting extended text alongside a roman typeface.

With that in mind, Mazon aims to be a light, open, low-contrast typeface, suitable for setting (extended) text, especially near Latin characters.  It was originally conceived of as a companion face to [ITC Mendoza Roman Std](http://www.fontshop.com/fonts/downloads/itc/itc_mendoza_roman_std_book).  To achieve these goals, Mazon features:

- Latinate, yet unobtrusive, serifs on many letters.
- Low contrast between horizontal and vertical strokes, with the horizontal ones
  being some 170% the thickness of the vertical ones.  cf. a classic Vilna-style
  face, such as [Ezra SIL](http://scripts.sil.org/EzraSIL_Home) with a 425%
  difference and Mendoza Roman, whose book weight sports a contrast of 120% -
  150% depending on the letter.
- A narrower design.  Even letters which are iconically square (e.g., mem sofit)
  are shy of the 1:1 ratio, about 90% as wide as they are tall,
  in order to emphasize the relationship with the Latin characters' vertical
  motion.
- A "two-thirds" height.  The height of the Hebrew characters lies between the
  x-height and the ascender/capital height of the roman, so that it is easily
  miscible inline with roman characters, without disturbing the vertical
  rhythm of the line too much.

# Development

## Software

Several pieces of software have been used to help develop Mazon.  These may be of interest to persons attempting to manipulate the Font Software.  They also deserve mention not only for their contribution to Mazon's creation, but as valuable members of the FLOSS world, without which the development of Mazon would have been, at best, much more expensive, and at worst, impossible.

- [Inkscape](http://www.inkscape.org) is used to draw the individual glyphs of
  the font, and saves them as individual vector graphics (`.svg`s).
- [FontForge](http://fontforge.org) collects the glyphs of the font, allows
  the user to edit various metrics about the font, and generates the final,
  usable font files.
    - NB.  The font is currently generated with version `20120731`, which is the
      stable binary distributed by Ubuntu (as of 5 Feb 2015).  There exists an
      updated fork (?) of FontForge located [here](http://fontforge.github.io).
      The way that this fontforge imports `.svg` files is *drastically different*
      and will produce an outline font.  I haven't experimented much, but I suspect
      that the way to accomodate the newer FontForge is to change the `.svg`s to
      have no stroke and a plain fill.
- [Python](http://www.python.org) is a scripting language used by Fontforge.
  It is used to generate a "rough draft" font, which can then be tuned further
  by hand in Fontforge.
- [git](http://git-scm.com) is used to manage the source files and maintain a
  history of revisions to the Mazon Hebrew source files.
- [Github](http://github.com) hosts the git repository for Mazon Hebrew.

## makefont.py

After editing the glyphs of the font (i.e., the material under the directories in `Draft Material`), you can regenerate the fonts by running `makefont.py` at the command line, provided Fontforge is installed on the computer.  The script will output two files into the root directory: `MazonHebrew-Regular.gen.sfd` and `MazonHebrew-Regular.gen.otf`.

Please note that the font produced by `makefont.py` is a relatively refined font.  All the niqqudot should be placed properly out-of-the-box and reasonable kerning defaults are applied.  But, the script will print out the string `"Failed to parse color"` about half a dozen times per glyph, so if you are concerned about clobbering your terminal with text, consider running the script with `2> /dev/null` (\*nix systems) or `2> nul` (Windows).

## Tests

### kernpairs

Running `kernpairs.py` will generate the file `kernpairs-stub.tex`, which contains the pairwise permutations of the alef-bet (*i.e.*, אא אב אג...בא בב בג...), along with a listing of the letter and all its niqqudot.  Subsequently running `xelatex kernpairs.tex` will yield a kerning specimen `kernpairs.pdf` for your perusal.

## Source files

### Layout

The following tree represents the layout of the Mazon Font Software source tree.

    .
    |-- Draft Material
    |   |-- basis.svg               // an empty, measured grid for new glyphs.
    |   |-- Letterforms
    |   |   `-- [...]               // individual glyphs, in .svg format.
    |   |-- Niqqudot
    |   |   `-- [...]               // individual glyphs, in .svg format.
    |   `-- Punctuation
    |       `-- [...]               // individual glyphs, in .svg format.
    |-- Tests
    |   |-- kernpairs.py            // generates kern testing sequences.
    |   `-- kernpairs.tex           // a XeLaTeX template for the sequences.
    |-- config.toml
    |-- FONTLOG.md                  // detailed information about the font.
    |-- LICENSE                     // the SIL Open Font License v1.1.
    |-- makefont.py                 // a python script for generating the fonts.
    |-- MazonHebrew-Regular.fea     // contains lookup/mark placement information.
    |-- MazonHebrew-Regular.otf     // a useable OpenType font.
    |-- MazonHebrew-Regular.sfd     // the Fontforge save file.
    `-- README.md                   // a brief introduction to the font.

The glyphs under the directories in `Draft Material` are named after their Unicode character names minus the code point, e.g., the file `full stop.svg` contains an illustration of the character `U+002E FULL STOP`, whereas `hebrew letter alef.svg` contains the same for `U+05D0 HEBREW LETTER ALEF`.  If you create additional glyphs, be sure to name them after their Unicode names.  This is both so others know what the glyph is supposed to represent and so that `makefont.py` can place the glyph appropriately in the font.

### Revision Control

The source files to Mazon are kept in a git repository, which can be found at
[https://github.com/hmc678/Mazon](https://github.com/hmc678/Mazon).

# Change Log

The following log lists changes from release to release.  Full history of the font and its files is available through `git log` and its variations.

* 5 February 2015 - v0.4
    - Adds support for horizontal kerning.
    - Fixes bearings on letters that are universally miskerned.
    - Adds support for the "furtive patah" feature.
    - Adds support for an alternate ayin when using niqqudot.
    - Improves spacing of nearly all niqqudot.
    - Straightens the leg on he.
    - Dramatically simplifies `makefont.py` by adding an Adobe Feature File,
      which allows the removal of a great deal of work in `makefont.py` as well
      as the bulk of the confusing configuration data in `config.toml`.
    - Adds the beginnings of a testing suite, which now includes a visual
      kerning pair table.
* 2 November 2014 - v0.3
    - Adds all of Hebrew's diacritical vowels (niqqudot).
    - Configuration data is now available for easier consumption in the
      file `config.toml`.
    - Many improvements to `makefont.py`, which now can create lookup tables,
      add anchors, and adjust glyph metrics according to its configuration
      data.
* 25 October 2014 - v0.2
    - Initial public release.
    - Most typographic punctuation are now available.  The remaining marks,
      to implement, or at least those which seem rather important to me, are:
        - `U+0023 NUMBER SIGN`
        - `U+0026 AMPERSAND`
        - `U+0040 COMMERCIAL AT`
        - `U+007E TILDE`
        - `U+00A7 SECTION SIGN`
        - `U+00AB LEFT-POINTING DOUBLE ANGLE QUOTATION MARK`
        - `U+00B6 PILCROW SIGN`
        - `U+00BB RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK`
        - `U+00D7 MULTIPLICATION SIGN`
        - `U+2007 FIGURE SPACE`
        - `U+2008 PUNCTUATION SPACE`
        - `U+2020 DAGGER`
        - `U+2021 DOUBLE DAGGER`
    - Note that, for the sake of this release, "punctuation marks" does not
      include niqqud, Hebrew's system of diacritical vowels.  Nor does it
      include ta'amei miqra, the cantillation marks found in Biblical texts.
      Numerical figures are also missing.
    - A build script, `makefont.py`, is also now available.
    - The qof now has a more rounded right arm.
    - Ayin is more balanced.
    - The ascender of lamed is reshaped ("more square")
    - The alternate (niqqud) ayin and an alef-lamed ligature are added.
* 16 October 2014 - v0.1
    - Initial (private) release.
    - Contains letterforms, but no punctuation.

# Acknowledgements

Mazon Hebrew was created by Ryan Dorsey in Winter 2014.

If you make modifications be sure to add your name (N), email (E), web-address (if you have one) (W) and description (D). This list is in alphabetical order.

    N: Ryan Dorsey
    E: ryanjdorsey at gmail dot com
    W: None
    D: Designer and Owner

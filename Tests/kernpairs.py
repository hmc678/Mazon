#!/usr/bin/env python3

letters = [chr(c) for c in list(range(0x05d0, 0x05ea + 1)) + [0xf300, 0xf301, 0xf302, 0xfb20, 0xfb4f]]
niqqudot = [chr(c) for c in list(range(0x05b0, 0x05bd + 1)) + [0x05c7]]

with open('kernpairs-stub.tex', 'w') as outfile:
    for ch1 in letters:
        outfile.write('\\section{{{}}}\n'.format(ch1))
        for ch2 in letters + niqqudot:
            outfile.write(ch1 + ch2 + ' ')
        outfile.write('\n\n')

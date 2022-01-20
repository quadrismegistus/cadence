#!/usr/bin/env python3
# -*- coding: utf-8 -*-

VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))

__all__ = [
        'format',
        'fullwidth',
        'styles',
        'FACE_PLAIN',
        'FACE_BOLD',
        'FACE_ITAL',
        'STYLE_SANS',
        'STYLE_SERIF',
        'STYLE_MONO',
        'STYLE_SCRIPT',
        'STYLE_DOUBLE',
        'STYLE_FRAKTUR',
        'STYLE_SMALLCAPS',
        ]

FACE_PLAIN = 0x00
FACE_BOLD = 0x01
FACE_ITAL = 0x02

STYLE_SANS = 0x0100
STYLE_SERIF = 0x0200
STYLE_MONO = 0x0400
STYLE_SCRIPT = 0x0800
STYLE_DOUBLE = 0x1000
STYLE_FRAKTUR = 0x2000
STYLE_SMALLCAPS = 0x4000

styles = {
        "sans" : STYLE_SANS,
        "serif" : STYLE_SERIF,
        "mono" : STYLE_MONO,
        "script" : STYLE_SCRIPT,
        "double" : STYLE_DOUBLE,
        "fraktur" : STYLE_FRAKTUR,
        "smallcaps" : STYLE_SMALLCAPS,
        }

valid_combos = set((
        STYLE_MONO,
        STYLE_SERIF|FACE_ITAL,
        STYLE_SERIF|FACE_BOLD,
        STYLE_SERIF|FACE_ITAL|FACE_BOLD,
        STYLE_SANS,
        STYLE_SANS|FACE_ITAL,
        STYLE_SANS|FACE_BOLD,
        STYLE_SANS|FACE_ITAL|FACE_BOLD,
        STYLE_SCRIPT,
        STYLE_SCRIPT|FACE_BOLD,
        STYLE_DOUBLE,
        STYLE_FRAKTUR,
        STYLE_FRAKTUR|FACE_BOLD,
        STYLE_SMALLCAPS,
        ))

charmap = {}
for c in valid_combos:
    charmap[c] = {}

## We can only convert a subset of text, specifically A-Za-z0-9.
for i in range(0, 26):
    cap = chr(i + ord('A'))
    sml = chr(i + ord('a'))

    charmap[STYLE_MONO][cap] = chr(i + 0x1d670)
    charmap[STYLE_MONO][sml] = chr(i + 0x1d68a)

    # Use IT/it/BD/bd as shortcuts to the italicized/bolded letters
    # so we can then map the opposite style applied over them onto
    # bold+italic
    IT = charmap[STYLE_SERIF|FACE_ITAL][cap] = chr(i + 0x1d434)
    it = charmap[STYLE_SERIF|FACE_ITAL][sml] = chr(i + 0x1d44e)
    BD = charmap[STYLE_SERIF|FACE_BOLD][cap] = chr(i + 0x1d400)
    bd = charmap[STYLE_SERIF|FACE_BOLD][sml] = chr(i + 0x1d41a)

    charmap[STYLE_SERIF|FACE_BOLD][IT] = \
    charmap[STYLE_SERIF|FACE_ITAL][BD] = \
    charmap[STYLE_SERIF|FACE_BOLD|FACE_ITAL][cap] = chr(i + 0x1d468)
    charmap[STYLE_SERIF|FACE_BOLD][it] = \
    charmap[STYLE_SERIF|FACE_ITAL][bd] = \
    charmap[STYLE_SERIF|FACE_BOLD|FACE_ITAL][sml] = chr(i + 0x1d482)

    IT = charmap[STYLE_SANS|FACE_ITAL][cap] = chr(i + 0x1d608)
    it = charmap[STYLE_SANS|FACE_ITAL][sml] = chr(i + 0x1d622)
    BD = charmap[STYLE_SANS|FACE_BOLD][cap] = chr(i + 0x1d5d4)
    bd = charmap[STYLE_SANS|FACE_BOLD][sml] = chr(i + 0x1d5ee)

    charmap[STYLE_SANS][cap] = chr(i + 0x1d5a0)
    charmap[STYLE_SANS][sml] = chr(i + 0x1d5ba)

    charmap[STYLE_SANS|FACE_BOLD][IT] = \
    charmap[STYLE_SANS|FACE_ITAL][BD] = \
    charmap[STYLE_SANS|FACE_BOLD|FACE_ITAL][cap] = chr(i + 0x1d63c)
    charmap[STYLE_SANS|FACE_BOLD][it] = \
    charmap[STYLE_SANS|FACE_ITAL][bd] = \
    charmap[STYLE_SANS|FACE_BOLD|FACE_ITAL][sml] = chr(i + 0x1d656)

    charmap[STYLE_SCRIPT][cap] = chr(i + 0x1d49c)
    charmap[STYLE_SCRIPT][sml] = chr(i + 0x1d4b6)
    charmap[STYLE_SCRIPT|FACE_BOLD][cap] = chr(i + 0x1d4d0)
    charmap[STYLE_SCRIPT|FACE_BOLD][sml] = chr(i + 0x1d4ea)

    charmap[STYLE_DOUBLE][cap] = chr(i + 0x1d538)
    charmap[STYLE_DOUBLE][sml] = chr(i + 0x1d552)

    charmap[STYLE_FRAKTUR][cap] = chr(i + 0x1d504)
    charmap[STYLE_FRAKTUR][sml] = chr(i + 0x1d51e)
    charmap[STYLE_FRAKTUR|FACE_BOLD][cap] = chr(i + 0x1d56c)
    charmap[STYLE_FRAKTUR|FACE_BOLD][sml] = chr(i + 0x1d586)

    charmap[STYLE_SMALLCAPS][cap] = cap

for i in range(0, 10):
    d = chr(i + ord('0'))
    charmap[STYLE_MONO][d] = chr(i + 0x1d7f6)
    charmap[STYLE_SERIF|FACE_BOLD][d] = chr(i + 0x1d7ce)
    charmap[STYLE_SANS|FACE_BOLD][d] = chr(i + 0x1d7ec)
    charmap[STYLE_DOUBLE][d] = chr(i + 0x1d7d8)
    charmap[STYLE_SANS][d] = chr(i + 0x1d7e2)

# Not all glyphs are in nice codepoint sequence, patch the gaps here
charmap[STYLE_SERIF|FACE_ITAL]["h"] = chr(0x210e)
charmap[STYLE_SCRIPT]["B"] = chr(0x212c)
charmap[STYLE_SCRIPT]["E"] = chr(0x2130)
charmap[STYLE_SCRIPT]["F"] = chr(0x2131)
charmap[STYLE_SCRIPT]["H"] = chr(0x210b)
charmap[STYLE_SCRIPT]["I"] = chr(0x2110)
charmap[STYLE_SCRIPT]["L"] = chr(0x2112)
charmap[STYLE_SCRIPT]["M"] = chr(0x2133)
charmap[STYLE_SCRIPT]["R"] = chr(0x2113)
charmap[STYLE_SCRIPT]["e"] = chr(0x212f)
charmap[STYLE_SCRIPT]["g"] = chr(0x210a)
charmap[STYLE_SCRIPT]["o"] = chr(0x2134)
charmap[STYLE_DOUBLE]["C"] = chr(0x2102)
charmap[STYLE_DOUBLE]["H"] = chr(0x210d)
charmap[STYLE_DOUBLE]["N"] = chr(0x2115)
charmap[STYLE_DOUBLE]["P"] = chr(0x2119)
charmap[STYLE_DOUBLE]["Q"] = chr(0x211a)
charmap[STYLE_DOUBLE]["R"] = chr(0x211d)
charmap[STYLE_DOUBLE]["Z"] = chr(0x2124)
charmap[STYLE_FRAKTUR]["C"] = chr(0x212d)
charmap[STYLE_FRAKTUR]["H"] = chr(0x210c)
charmap[STYLE_FRAKTUR]["I"] = chr(0x2111)
charmap[STYLE_FRAKTUR]["R"] = chr(0x211c)
charmap[STYLE_FRAKTUR]["Z"] = chr(0x2128)

# And smallcaps are all over the place
charmap[STYLE_SMALLCAPS]["a"] = chr(0x1d00)
charmap[STYLE_SMALLCAPS]["b"] = chr(0x0299)
charmap[STYLE_SMALLCAPS]["c"] = chr(0x1d04)
charmap[STYLE_SMALLCAPS]["d"] = chr(0x1d05)
charmap[STYLE_SMALLCAPS]["e"] = chr(0x1d07)
charmap[STYLE_SMALLCAPS]["f"] = chr(0xa730)
charmap[STYLE_SMALLCAPS]["g"] = chr(0x0262)
charmap[STYLE_SMALLCAPS]["h"] = chr(0x029c)
charmap[STYLE_SMALLCAPS]["i"] = chr(0x026a)
charmap[STYLE_SMALLCAPS]["j"] = chr(0x1d0a)
charmap[STYLE_SMALLCAPS]["k"] = chr(0x1d0b)
charmap[STYLE_SMALLCAPS]["l"] = chr(0x029f)
charmap[STYLE_SMALLCAPS]["m"] = chr(0x1d0d)
charmap[STYLE_SMALLCAPS]["n"] = chr(0x0274)
charmap[STYLE_SMALLCAPS]["o"] = chr(0x1d0f)
charmap[STYLE_SMALLCAPS]["p"] = chr(0x1d18)
charmap[STYLE_SMALLCAPS]["q"] = "Q" # Can't find this one anywhere
charmap[STYLE_SMALLCAPS]["r"] = chr(0x0280)
charmap[STYLE_SMALLCAPS]["s"] = chr(0xa731)
charmap[STYLE_SMALLCAPS]["t"] = chr(0x1d1b)
charmap[STYLE_SMALLCAPS]["u"] = chr(0x1d1c)
charmap[STYLE_SMALLCAPS]["v"] = chr(0x1d20)
charmap[STYLE_SMALLCAPS]["w"] = chr(0x1d21)
charmap[STYLE_SMALLCAPS]["x"] = "x"
charmap[STYLE_SMALLCAPS]["y"] = chr(0x028f)
charmap[STYLE_SMALLCAPS]["z"] = chr(0x1d22)


def format(fmt, st):
    """\
    Return the formatted verison of the given string.
    """
    ret = ""
    if not st: return ret
    if fmt not in valid_combos:
        return st
    cm = charmap[fmt]
    for c in st:
        ret += cm.get(c, c)
    return ret

def fullwidth(st):
    """\
    Return the fullwidth version of the given string.
    """
    ret = ""
    if not st: return ret
    for c in st:
        i = ord(c)
        if c == " ":
            ret += chr(0x3000)
        elif 0x21 <= i <= 0x7f:
            ret += chr(i - 0x21 + 0xff01)
        else:
            ret += c
    return ret

# Self-test routine
if __name__ == '__main__':

    style_names = { styles[k]:k for k in styles.keys() }
    combo_names = {}
    longest_name = 0
    for c in valid_combos:
        sty = c & ~0xFF
        cn = style_names[sty]
        if c & FACE_BOLD:
            cn += " bold"
        if c & FACE_ITAL:
            cn += " ital"
        combo_names[c] = cn
        longest_name = max(longest_name, len(cn))

    name_fmt = "{{:>{0}s}}: ".format(longest_name)

    for c in valid_combos:
        print(name_fmt.format(combo_names[c]), end="")
        print(format(c,
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"))

    print(format(STYLE_SANS|FACE_ITAL|FACE_BOLD,
        "pre-combined bold and italic"))
    print(format(STYLE_SANS|FACE_ITAL,
        format(STYLE_SANS|FACE_BOLD, "Chained bold and italic")
        ))

#
# Editor modelines - http://www.wireshark.org/tools/modelines.html
#
# Local variables:
# c-basic-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# End:
#
# vi:set shiftwidth=4 tabstop=4 expandtab:
# indentSize=4:tabSize=4:noTabs=true:
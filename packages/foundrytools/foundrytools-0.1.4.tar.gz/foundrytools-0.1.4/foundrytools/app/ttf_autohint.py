from io import BytesIO

from fontTools.ttLib import TTFont
from ttfautohint import ttfautohint

from foundrytools import Font
from foundrytools.constants import T_HEAD


class TTFAutohintError(Exception):
    """An error that occurred during TrueType auto-hinting."""


def run(font: Font) -> bool:
    """
    Autohint a TrueType font.

    :param font: The Font object to autohint.
    :type font: Font
    :raises NotImplementedError: If the font is not a TrueType font.
    :raises TTFAutohintError: If an error occurred during autohinting.
    """
    if not font.is_tt:
        raise NotImplementedError("Not a TrueType font.")

    try:
        with BytesIO() as buffer:
            flavor = font.ttfont.flavor
            font.ttfont.flavor = None
            font.save(buffer, reorder_tables=None)
            data = ttfautohint(in_buffer=buffer.getvalue(), no_info=True)
            hinted_font = TTFont(BytesIO(data), recalcTimestamp=False)
            hinted_font[T_HEAD].modified = font.t_head.modified_timestamp
            font.ttfont = hinted_font
            font.ttfont.flavor = flavor
            return True
    except Exception as e:
        raise TTFAutohintError(e) from e

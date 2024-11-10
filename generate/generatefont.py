#gemini

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

font = TTFont()
# ... (add and populate tables as mentioned above)

glyph = font['glyf']['A'] = TTGlyph()
pen = TTGlyphPen(glyph)
pen.moveTo((0, 0))
pen.lineTo((100, 0))
pen.lineTo((50, 100))
pen.closePath()

font.save("myfont.ttf")

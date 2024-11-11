#gemini

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from PIL import Image, ImageDraw, ImageFont



def print_glyph(font_path, glyph_name):
    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    glyph = glyph_set[glyph_name]

    pen = TTGlyphPen(glyph_set)
    glyph.draw(pen)
    print(pen.glyph())

INPUT_PATH = "C:/Windows/Fonts/arial.ttf"
OUTPUT_PATH = "./output/arial_transformed.ttf"

with TTFont(INPUT_PATH) as f:
    glyfTable = f["glyf"]
    glyphSet = f.getGlyphSet()
    for glyphName in glyphSet.keys():
        print(glyphName)
        if (glyphName == "A"):
            glyph = glyphSet[glyphName]
            # create new TTGlyph from Path
            pen = TTGlyphPen(None)
            pen.moveTo((0, 0))
            pen.lineTo((100, 0))
            pen.lineTo((50, 100))
            pen.closePath()
            glyph.draw(pen)
#            glyfTable[glyphName] = pen.glyph()
            print(pen.glyph())
            print(pen.glyph().getCoordinates(glyfTable))
            break
#    f["A"] = pen.glyph()
    
#    print_glyph(INPUT_PATH, "AAAA")
    f.save(OUTPUT_PATH)
    print_glyph(OUTPUT_PATH, "A")



# Load the font
font = ImageFont.truetype(OUTPUT_PATH, 24)  # Replace "your_font.ttf" with the path to your font file

# Create an image
image = Image.new("RGB", (200, 50), "white")
draw = ImageDraw.Draw(image)

# Draw the text
text = "A world"
draw.text((10, 10), text, font=font, fill="black")

# Save the image
image.save("./output/testFont.png")



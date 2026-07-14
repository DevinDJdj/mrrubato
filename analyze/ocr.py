#pip install pytesseract
#pip install pillow
import pytesseract
from PIL import Image

# Load the image
#img = Image.open('../extensions/trey/example-webkit.png')
img = Image.open('../shot1.jpg')
#very dependent on page as to what will work and what not.  
#simple google search page works quite well with just white background and black text.
#more complex pages with images and colors and different fonts are much harder.

# Get detailed OCR data
data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

# Loop through the detected words and print their positions
n_boxes = len(data['text'])
prevbox = {"x":0, "y":0, "w":0, "h":0}
currentbox = {"x":0, "y":0, "w":0, "h":0}
prevconf = 0
currentline = ""
for i in range(n_boxes):
    if int(data['conf'][i]) > 60 or prevconf > 60:  # Filter by confidence
        prevconf = int(data['conf'][i])
        text = data['text'][i]

        #seems to come in order.  
        if (text.strip() == ""):
            continue

        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
        
        if (prevbox["x"]+prevbox["w"]+40 > x and prevbox["y"]+prevbox["h"] > y and prevbox["y"]-prevbox["h"] < y):
            #same line

            currentline += " " + text
            currentbox = {"x":min(prevbox["x"], x), "y":min(prevbox["y"], y), "w":0, "h":0}
            currentbox["w"] = max(prevbox["x"]+prevbox["w"], x+w) - currentbox["x"]
            currentbox["h"] = max(prevbox["y"]+prevbox["h"], y+h) - currentbox["y"]
        else:
            if (currentline != ""):
                print("LINE: " + currentline)
                print(f"Position: (x={currentbox['x']}, y={currentbox['y']}, w={currentbox['w']}, h={currentbox['h']})")
            currentline = text
            currentbox = {"x":x, "y":y, "w":w, "h":h}
        prevbox = {"x":x, "y":y, "w":w, "h":h}

        print(f"Text: '{text}', Position: (x={x}, y={y}, w={w}, h={h}, block_num={data['block_num'][i]}, par_num={data['par_num'][i]}, line_num={data['line_num'][i]}, word_num={data['word_num'][i]}, conf={data['conf'][i]})")

if (currentline != ""):
    print("LINE: " + currentline)

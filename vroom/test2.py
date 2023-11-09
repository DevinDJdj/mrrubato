import qrcode
import platform

#generate contextual information for Documentation for customer as well as historical context of user actions perhaps.  

def os_info():
    ret = platform.system()
    ret = ret + ' ' + platform.release()
    ret = ret + ' ' + platform.version()
    return ret
    


qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=3, #this controls size
    border=2,
)
qr.add_data(os_info())
#qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
    
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")

    
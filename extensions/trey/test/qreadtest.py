import cv2
from qreader import QReader
import numpy as np
import logging

logger = logging.getLogger(__name__)
if __name__ == "__main__":

    qreader = QReader()
    img = cv2.imread("test_qr.png")
    print(img.shape)
    image = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    decoded_texts = qreader.detect_and_decode(image=image)
    if decoded_texts:
        for text in decoded_texts:
            print(f"QR Code data: {text}")
            logger.info(f"QR Code data: {text}")
    else:
        print("No QR code detected.")

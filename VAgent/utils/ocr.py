import easyocr
from surya.detection import batch_inference
from surya.model.segformer import load_model, load_processor
import cv2
import numpy as np
from pytesseract import pytesseract

def easyocr_get_text(img):
    # convert to np.array
    img = np.array(img)
    
    # create reader
    reader = easyocr.Reader(['ch_sim','en']) 
    
    # read image
    result = reader.readtext(img)
    
    # result
    result_str = ""
    for i in result:
        word = i[1]
        result_str += f"\n{word}"
    return result_str

def surya_get_text(img):
    model, processor = load_model(), load_processor()

    # predictions is a list of dicts, one per image
    predictions = batch_inference([img], model, processor)
    
    return predictions[0]

def pytesseract_get_text(img):
    # Convert PIL Image to NumPy array
    img_array = np.array(img)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to get the text from the image
    text = pytesseract.image_to_string(gray)

    return text
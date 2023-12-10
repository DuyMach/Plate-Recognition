import easyocr
from PIL import Image as img
from PIL import ImageDraw as imgDraw
import numpy as np
import torch
import re
import pytesseract
import requests
import os

def validate_license_plate(license_plate, all_plate_numbers):
    for plate_number in all_plate_numbers:
        if re.search(plate_number, cleaned_license_plate):
            return True
    return False
    
    
def insert_license_plate(license_plate):
    url = "http://localhost:3001/insert_license_plate"
    data = {"license_plate" : license_plate}

    response = requests.post(url, json=data)
    if response.status_code == 200:
        print(f"License plate {license_plate} inserted itno the databased")
        return True
    else:
        print(f"Error: {response.status_code}")
        return False

def get_all_plate_numbers():
    url = "http://localhost:3001/get_all_plate_numbers"

    response = requests.get(url)
    if response.status_code == 200:
        plate_numbers = response.json().get("plate_numbers")
        return plate_numbers
    else:
        print(f"Error: {response.status_code}")
        return None


# load yolov5 model
model_path = r'C:\Users\Owner\source\repos\Plate-Recognition\yolov5' # path to local yolov5 installation
weights = r'C:\Users\Owner\source\repos\Plate-Recognition\best.pt' # path to weights file
model = torch.hub.load(model_path, 'custom', path=weights, source='local').to('cpu') #using cpu
input_dir = r'C:\Users\Owner\source\repos\Plate-Recognition\data2'

# load image for yolov5 model
for img_name in os.listdir(input_dir): 
    img_path =os.path.join(input_dir, img_name) 
    image = img.open(img_path).convert("RGB") # image converted to RGB

    # Create a drawing object
    draw = imgDraw.Draw(image)

    #load the list of valid plates, this is where we would download the database, or stream it
    valid_plates = 'AN74043'
    expired_plates = ['EXPIRED']
    all_plate_numbers = get_all_plate_numbers()

    # use the model on the selected image 
    results = model(image)

    # Create an EasyOCR reader of the english character dataset 
    reader = easyocr.Reader(['en'])

    # results.xyxy returns a list of lists where each contain [[x_min, y_min, x_max, y_max, confidence, class]]
    for detection in results.xyxy[0]: # [0] dives one layer further
        confidenceRating = float(detection[4])

        if confidenceRating > .75:
            #get the coordinates of the detection
            x_min = int(detection[0])
            y_min = int(detection[1])
            x_max = int(detection[2])
            y_max = int(detection[3])

            # Crop the detection for OCR preparation
            crop = image.crop((x_min, y_min, x_max, y_max))

            # read the cropped image with ocr reader, crop detect is a tuple consisting of (string/text,(x,y,w,h))
            crop_detect = reader.readtext(np.array(crop))

            # Initialize an empty list to store all text strings
            all_detected_text = []

            # put all detections in a single array
            for detection in crop_detect: 
                all_detected_text.append(detection[1])

            full_plate = ' '.join(all_detected_text)
            cleaned_license_plate = full_plate.replace(" ", "").replace("-", "")

            if validate_license_plate(cleaned_license_plate, all_plate_numbers):
                draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=9)
            else:
                draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=5)

    #shows the image with all markups
    image.show()
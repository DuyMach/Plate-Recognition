import easyocr
from PIL import Image as img
from PIL import ImageDraw as imgDraw
import numpy as np
import torch
from fuzzywuzzy import fuzz

# load yolov5 model for liscense plate detection
model_path = 'E:\Admin\Documents\AI_project\LP2\yolov5' # path to local yolov5 installation
weights = 'E:\Admin\Documents\AI_project\LP2\code\\plate.pt' # path to weights file
model = torch.hub.load(model_path, 'custom', path=weights, source='local').to('cpu') #using cpu

# load image for yolov5 model
image_path = 'E:\Admin\Documents\AI_project\LP2\code\\test2.jpg'  # Path to image 
image = img.open(image_path).convert("RGB") # image converted to RGB

# Create a drawing object
draw = imgDraw.Draw(image)

#load the list of valid plates, this is where we would download the database, or stream it
valid_plates = ['284FH8']
expired_plates = ['EXPIRED']

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

        # Convert the cropped image to grayscale
        greyscale = crop.convert("L")

        # read the cropped image with ocr reader, crop detect is a tuple consisting of (string/text,(x,y,w,h))
        crop_detect = reader.readtext(np.array(greyscale))

        # Initialize an empty list to store all text strings
        all_detected_text = []

        # put all detections in a single array
        for detection in crop_detect: 
            all_detected_text.append(detection[1])

        #clean all text into a string 
        temp = "".join(all_detected_text)
        cleaned_text = ""
        for i in temp:
            if i.isdigit() or i.isalpha():
                cleaned_text += i
        cleaned_text.replace(" ", "")

        threshold = 80
        highest_match_ratio = 0
        for plate in valid_plates:
            if len(plate) == len(cleaned_text):
                ratio =  fuzz.ratio(cleaned_text.upper(), plate.upper())
            else:
                for i in range(len(cleaned_text) - len(plate) + 1):
                    substring = cleaned_text[i:i+len(plate)]
                    ratio = fuzz.ratio(substring.upper(), plate.upper())

                    if ratio > highest_match_ratio:
                        highest_match_ratio = ratio

        #will make its decision based on the highest match ratio 
        if highest_match_ratio > threshold:
            draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=9)
        else: 
            draw.rectangle([x_min, y_min, x_max, y_max], outline="red", width=5)
        
           
#shows the image with all markups
image.show()



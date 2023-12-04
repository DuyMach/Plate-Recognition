import os

import cv2
import numpy as np
import matplotlib.pyplot as plt
import easyocr
import requests

import util


# define constants
model_cfg_path = os.path.join('.', 'model', 'cfg', 'yolov3.cfg')
model_weights_path = os.path.join('.', 'model', 'weights', 'yolov3.weights')
class_names_path = os.path.join('.', 'model', 'class.names')

input_dir = r'C:\Users\Owner\source\repos\Plate-Recognition\data'

def validate_license_plate(license_plate):
    url = "http://localhost:3001/validate_license_plate"
    data = {"license_plate" : license_plate}

    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json().get("results")
        return result
    else:
        print(f"Error: {response.status_code}")
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

for img_name in os.listdir(input_dir): 
    img_path =os.path.join(input_dir, img_name)

    # load class names
    with open(class_names_path, 'r') as f:
        class_names = [j[:-1] for j in f.readlines() if len(j) > 2]
        f.close()

    # load model
    net = cv2.dnn.readNetFromDarknet(model_cfg_path, model_weights_path)

    # load image

    img = cv2.imread(img_path)

    H, W, _ = img.shape

    # convert image
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), True)

    # get detections
    net.setInput(blob)

    detections = util.get_outputs(net)

    # bboxes, class_ids, confidences
    bboxes = []
    class_ids = []
    scores = []

    for detection in detections:
        # [x1, x2, x3, x4, x5, x6, ..., x85]
        bbox = detection[:4]

        xc, yc, w, h = bbox
        bbox = [int(xc * W), int(yc * H), int(w * W), int(h * H)]

        bbox_confidence = detection[4]

        class_id = np.argmax(detection[5:])
        score = np.amax(detection[5:])

        bboxes.append(bbox)
        class_ids.append(class_id)
        scores.append(score)

    # apply nms
    bboxes, class_ids, scores = util.NMS(bboxes, class_ids, scores)

    # plot
    reader = easyocr.Reader(['en'])
    for bbox_, bbox in enumerate(bboxes):
        xc, yc, w, h = bbox

        license_plate = img[int(yc - (h / 2)):int(yc + (h / 2)),
                             int(xc - (w / 2)):int(xc + (w / 2))].copy()

        img = cv2.rectangle(img,
                            (int(xc - (w / 2)), int(yc - (h / 2))),
                            (int(xc + (w / 2)), int(yc + (h / 2))),
                            (0, 255, 0),
                            10)
        
        license_plate_gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

        _, license_plate_thresh = cv2.threshold(license_plate_gray, 64, 255, cv2.THRESH_BINARY_INV)

        output = reader.readtext(license_plate_gray)
        
        for out in output: 
            text_bbox, text, text_score = out
            print(text, text_score)
            cleaned_license_plate = text.replace(" ", "").replace("-", "")
            validation_result = validate_license_plate(cleaned_license_plate)

            if validation_result:
                print(f"{text} is a valid plate.")
            else:
                print(f"{text} is a not valid plate.")

                insert_success = insert_license_plate(cleaned_license_plate)
                if insert_success:
                    print(f"License plate {text} inserted itno the databased")

        
    plt.figure()
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate_gray, cv2.COLOR_BGR2RGB))

    plt.figure()
    plt.imshow(cv2.cvtColor(license_plate_thresh, cv2.COLOR_BGR2RGB))
    plt.show()

import torch
from PIL import Image as img
from PIL import Image as imgDraw


# LOAD YOLO MODEL ------------------------------------------------------------------------
modelPath = 'E:\Admin\Documents\AI_project\LP2\yolov5' # path to local yolov5 installation
weights = 'E:\Admin\Documents\AI_project\LP2\code\\best.pt' # path to weights file

model = torch.hub.load(modelPath, 'custom', path=weights, source='local')  # local repo
# ----------------------------------------------------------------------------------------

# LOAD MEDIA -----------------------------------------------------------------------------
imagePath = 'E:\Admin\Documents\AI_project\LP2\code\\test4.jpg'  # Path to image 
image = img.open(imagePath).convert("RGB") # image converted to RGB
# ----------------------------------------------------------------------------------------

# Perform inference
results = model(image)

# Display the results
results.show()

# Draw bounding boxes on the image
draw = imgDraw.Draw(image)
for detection in results.xyxy[0]:
    class_id = int(detection[5])
    confidence = float(detection[4])

    if confidence > 0.5:  # Adjust confidence threshold as needed
        x, y, w, h = map(int, detection[:4])
        draw.rectangle([x, y, w, h], outline="red", width=2)

# Save or display the image with bounding boxes
image.show()
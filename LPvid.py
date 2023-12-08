import torch
import cv2
from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np

# LOAD YOLO MODEL ------------------------------------------------------------------------
modelPath = 'E:\Admin\Documents\AI_project\LP2\yolov5'  # path to local yolov5 installation
weights = 'E:\Admin\Documents\AI_project\LP2\code\\best.pt'  # path to weights file

model = torch.hub.load(modelPath, 'custom', path=weights, source='local')  # local repo
# ----------------------------------------------------------------------------------------

# LOAD VIDEO -----------------------------------------------------------------------------
video_path = 'E:\Admin\Documents\AI_project\LP2\code\\testvid(2).mp4'  # Path to video
output_path = 'E:\Admin\Documents\AI_project\LP2\code\output.mp4'  # Path to output video

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
# ----------------------------------------------------------------------------------------

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Perform inference
    results = model(pil_image)

    # Draw bounding boxes on the frame
    draw = ImageDraw.Draw(pil_image)
    for detection in results.xyxy[0]:
        class_id = int(detection[5])
        confidence = float(detection[4])

        if confidence > 0.5:  # Adjust confidence threshold as needed
            x, y, w, h = map(int, detection[:4])
            draw.rectangle([x, y, w, h], outline="red", width=2)

    # Convert the PIL Image back to OpenCV format
    frame_with_boxes = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Write the frame with bounding boxes to the output video
    out.write(frame_with_boxes)

    # Display the frame with bounding boxes (optional)
    cv2.imshow('Frame', frame_with_boxes)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

from ultralytics import YOLO
model = YOLO("yolov8m.pt")

results = model.predict("images/Screenshot 2024-09-16 at 12.57.32 PM.png")

result = results[0]
print(len(result.boxes))
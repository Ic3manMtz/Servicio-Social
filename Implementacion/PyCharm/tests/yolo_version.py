from ultralytics import YOLO

print (YOLO().model.names)
model = YOLO("yolov11m.pt")
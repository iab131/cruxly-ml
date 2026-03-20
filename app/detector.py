from ultralytics import YOLO

# Load pretrained model (COCO for now)
model = YOLO("yolov8n.pt")

def detect_holds(image_path):
    results = model(image_path)

    boxes = []
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            boxes.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })

    return boxes

holds = [
    {"x": 100, "y": 500, "color": "red"},
    {"x": 150, "y": 400, "color": "red"},
    {"x": 200, "y": 300, "color": "red"},
]
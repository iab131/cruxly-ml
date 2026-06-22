from pathlib import Path

from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "runs" / "detect" / "vehicle_detector-3" / "weights" / "best.pt"

DEFAULT_CONF = 0.25
DEFAULT_IOU = 0.45
DEFAULT_MAX_DET = 300

model = YOLO(str(DEFAULT_MODEL_PATH))


def detect(image_path, conf=DEFAULT_CONF, iou=DEFAULT_IOU, max_det=DEFAULT_MAX_DET):
    results = model.predict(
        source=str(image_path),
        conf=conf,
        iou=iou,
        max_det=max_det,
        verbose=False,
    )

    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = float(box.conf[0]) if box.conf is not None else None
            class_id = int(box.cls[0]) if box.cls is not None else None

            detections.append(
                {
                    "x1": float(x1),
                    "y1": float(y1),
                    "x2": float(x2),
                    "y2": float(y2),
                    "confidence": confidence,
                    "class_id": class_id,
                }
            )

    return detections


def detect_holds(image_path):
    return detect(image_path)

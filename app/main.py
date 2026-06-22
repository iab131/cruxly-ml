from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
import cv2
from pydantic import BaseModel

from app import detector
from app.route_solver import build_graph, find_route
from app.utils import draw_debug_overlay


app = FastAPI()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
STATIC_DIR = PROJECT_ROOT / "static"
MAX_BOX_AREA_RATIO = 0.20
MAX_BOX_WIDTH_RATIO = 0.40
MAX_BOX_HEIGHT_RATIO = 0.40
MIN_BOX_SIZE = 5
MIN_BOX_AREA = 25


class ManualHold(BaseModel):
    id: int
    x: float
    y: float
    color: str | None = None
    type: str | None = None


class ManualSolveRequest(BaseModel):
    holds: list[ManualHold]


def detections_to_holds(detections):
    holds = []
    for index, detection in enumerate(detections):
        x1 = detection["x1"]
        y1 = detection["y1"]
        x2 = detection["x2"]
        y2 = detection["y2"]

        holds.append(
            {
                "id": index,
                "x": (x1 + x2) / 2,
                "y": (y1 + y2) / 2,
                "width": x2 - x1,
                "height": y2 - y1,
                "confidence": detection["confidence"],
                "class_id": detection["class_id"],
            }
        )

    return holds


def filter_detections(detections, image_width, image_height):
    accepted = []
    rejected_large = []
    image_area = image_width * image_height

    for detection in detections:
        width = detection["x2"] - detection["x1"]
        height = detection["y2"] - detection["y1"]
        area = width * height

        is_large = (
            area > image_area * MAX_BOX_AREA_RATIO
            or width > image_width * MAX_BOX_WIDTH_RATIO
            or height > image_height * MAX_BOX_HEIGHT_RATIO
        )
        is_tiny = width < MIN_BOX_SIZE or height < MIN_BOX_SIZE or area < MIN_BOX_AREA

        if is_large:
            rejected_large.append(detection)
            continue

        if is_tiny:
            continue

        accepted.append(detection)

    return accepted, rejected_large


def solve_holds(holds, max_reach=None):
    if max_reach is None:
        graph = build_graph(holds)
    else:
        graph = build_graph(holds, max_reach=max_reach)

    route_indices = find_route(graph, holds)
    return [holds[index] for index in route_indices]


@app.get("/")
async def root():
    return RedirectResponse(url="/manual")


@app.get("/manual")
async def manual_page():
    return FileResponse(STATIC_DIR / "manual.html")


@app.post("/solve")
async def solve(
    file: UploadFile,
    conf: float = detector.DEFAULT_CONF,
    iou: float = detector.DEFAULT_IOU,
    max_det: int = detector.DEFAULT_MAX_DET,
    debug: bool = False,
):
    suffix = Path(file.filename or "").suffix or ".jpg"

    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(await file.read())

    try:
        image = cv2.imread(str(temp_path))
        if image is None:
            raise ValueError(f"Could not read uploaded image: {file.filename}")

        image_height, image_width = image.shape[:2]
        raw_detections = detector.detect(temp_path, conf=conf, iou=iou, max_det=max_det)
        filtered_detections, rejected_large_boxes = filter_detections(
            raw_detections,
            image_width,
            image_height,
        )
        holds = detections_to_holds(filtered_detections)

        route = solve_holds(holds)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        overlay_path = OUTPUT_DIR / f"solve_{timestamp}.jpg"
        draw_debug_overlay(
            temp_path,
            holds,
            route,
            overlay_path,
            rejected_large_boxes=rejected_large_boxes,
            debug=debug,
        )
        overlay_relative_path = overlay_path.relative_to(PROJECT_ROOT).as_posix()
    finally:
        temp_path.unlink(missing_ok=True)

    return {
        "holds": holds,
        "route": route,
        "overlay_path": overlay_relative_path,
        "debug": {
            "model_path": str(detector.DEFAULT_MODEL_PATH),
            "conf": conf,
            "iou": iou,
            "max_det": max_det,
            "raw_detection_count": len(raw_detections),
            "filtered_hold_count": len(holds),
            "removed_large_box_count": len(rejected_large_boxes),
            "image_width": image_width,
            "image_height": image_height,
            "hold_count": len(holds),
            "route_length": len(route),
        },
    }


@app.post("/solve_manual")
async def solve_manual(request: ManualSolveRequest, max_reach: float = 450):
    holds = [hold.dict() for hold in request.holds]
    route = solve_holds(holds, max_reach=max_reach)
    fallback_used = False

    if len(holds) > 1 and len(route) <= 1:
        route = sorted(holds, key=lambda hold: hold["y"], reverse=True)
        fallback_used = True

    return {
        "holds": holds,
        "route": route,
        "debug": {
            "route_length": len(route),
            "max_reach": max_reach,
            "fallback_used": fallback_used,
        },
    }

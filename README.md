# Cruxly ML

FastAPI service for detecting climbing holds in an uploaded image, solving a simple bottom-to-top route, and writing a debug overlay image.

## Install

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The default detector model is:

```text
runs/detect/vehicle_detector-3/weights/best.pt
```

## Run

```powershell
uvicorn app.main:app --reload
```

## Manual Hold Solver

Manual mode is the current reliable path while the detector is still rough.

Open this page with the server running:

```text
http://127.0.0.1:8000/manual
```

Upload a wall image, click holds to add them, click a hold again to delete it, then press **Solve Manual Holds**. The page sends your selected holds to `POST /solve_manual` and draws the returned route over the image. If no connected route is found within the current max reach, manual mode shows a bottom-to-top fallback path so you still get visible feedback.

## Test `/solve`

With the server running:

```powershell
python scripts/test_solve.py path\to\climbing_image.jpg
```

You can tune YOLO inference thresholds while debugging:

```powershell
python scripts/test_solve.py image.png --conf 0.1 --iou 0.4 --max-det 300
```

Or with curl:

```powershell
curl.exe -X POST http://127.0.0.1:8000/solve -F "file=@path\to\climbing_image.jpg"
```

The response includes detected holds, the selected route, debug counts, and an `overlay_path` pointing to an image under `outputs/`.

If the detector still finds only one huge box, the current `best.pt` is probably not a climbing-hold detector and we need to retrain with correctly labeled individual holds.

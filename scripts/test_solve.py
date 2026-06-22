import argparse
import json
from pathlib import Path
from urllib import parse
from urllib import request


def build_multipart(image_path):
    boundary = "----cruxly-ml-boundary"
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{image_path.name}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return boundary, header + image_path.read_bytes() + footer


def main():
    parser = argparse.ArgumentParser(description="Upload a local image to the /solve endpoint.")
    parser.add_argument("image", help="Path to a local climbing image")
    parser.add_argument("--url", default="http://127.0.0.1:8000/solve", help="Solve endpoint URL")
    parser.add_argument("--conf", type=float, default=None, help="YOLO confidence threshold")
    parser.add_argument("--iou", type=float, default=None, help="YOLO IoU threshold")
    parser.add_argument("--max-det", type=int, default=None, help="YOLO max detections")
    parser.add_argument("--debug", action="store_true", help="Draw rejected large boxes on the overlay")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    query = {}
    if args.conf is not None:
        query["conf"] = args.conf
    if args.iou is not None:
        query["iou"] = args.iou
    if args.max_det is not None:
        query["max_det"] = args.max_det
    if args.debug:
        query["debug"] = "true"

    url = args.url
    if query:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{parse.urlencode(query)}"

    boundary, body = build_multipart(image_path)
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    with request.urlopen(req) as response:
        payload = json.loads(response.read().decode("utf-8"))

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

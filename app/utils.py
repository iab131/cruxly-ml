import cv2


def draw_box(image, detection, color, thickness=2):
    x1 = int(round(detection["x1"]))
    y1 = int(round(detection["y1"]))
    x2 = int(round(detection["x2"]))
    y2 = int(round(detection["y2"]))
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)


def draw_debug_overlay(image_path, holds, route, output_path, rejected_large_boxes=None, debug=False):
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    route_lookup = {hold["id"]: order for order, hold in enumerate(route, start=1)}

    if debug:
        for detection in rejected_large_boxes or []:
            draw_box(image, detection, (0, 0, 255), 3)

    for hold in holds:
        x1 = int(round(hold["x"] - hold["width"] / 2))
        y1 = int(round(hold["y"] - hold["height"] / 2))
        x2 = int(round(hold["x"] + hold["width"] / 2))
        y2 = int(round(hold["y"] + hold["height"] / 2))

        color = (0, 255, 0)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        if hold["id"] in route_lookup:
            cv2.putText(
                image,
                str(route_lookup[hold["id"]]),
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
                cv2.LINE_AA,
            )

    for current_hold, next_hold in zip(route, route[1:]):
        start = (int(round(current_hold["x"])), int(round(current_hold["y"])))
        end = (int(round(next_hold["x"])), int(round(next_hold["y"])))
        cv2.line(image, start, end, (0, 255, 255), 3)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path

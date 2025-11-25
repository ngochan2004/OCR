import cv2
import numpy as np

def detect_boxes(image, model_path, min_confidence=0.5, min_size=10):
    h, w = image.shape[:2]
    new_w, new_h = (320, 320)

    blob = cv2.dnn.blobFromImage(image, 1.0, (new_w, new_h),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)

    net = cv2.dnn.readNet(model_path)
    net.setInput(blob)
    scores, geometry = net.forward(["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"])

    boxes, confidences = [], []

    for y in range(scores.shape[2]):
        for x in range(scores.shape[3]):
            score = scores[0, 0, y, x]
            if score < min_confidence:
                continue

            offsetX, offsetY = x * 4.0, y * 4.0
            angle = geometry[0, 4, y, x]
            cos, sin = np.cos(angle), np.sin(angle)
            h = geometry[0, 0, y, x] + geometry[0, 2, y, x]
            w = geometry[0, 1, y, x] + geometry[0, 3, y, x]

            endX = int(offsetX + cos * geometry[0, 1, y, x] + sin * geometry[0, 2, y, x])
            endY = int(offsetY - sin * geometry[0, 1, y, x] + cos * geometry[0, 2, y, x])
            startX = int(endX - w)
            startY = int(endY - h)

            if w < min_size or h < min_size:
                continue

            boxes.append((startX, startY, int(w), int(h)))
            confidences.append(float(score))

    indices = cv2.dnn.NMSBoxes(
        [[x, y, w, h] for x, y, w, h in boxes],
        confidences,
        min_confidence,
        0.4
    )

    final_boxes = [boxes[i[0]] for i in indices] if len(indices) > 0 else []
    return final_boxes

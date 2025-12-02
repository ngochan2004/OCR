import numpy as np
import difflib

def compute_iou(boxA, boxB):
    # box: [x, y, w, h]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
    return iou

def evaluate_metrics(gt_boxes, pred_boxes, gt_text, pred_text, iou_threshold=0.5):
    """
    gt_boxes: list of [x, y, w, h]
    pred_boxes: list of [x, y, w, h]
    gt_text: full ground truth text string
    pred_text: full predicted text string
    """
    metrics = {
        "precision": 0.0,
        "recall": 0.0,
        "hmean": 0.0,  # F-score
        "iou_average": 0.0,
        "char_accuracy": 0.0,
        "edit_distance": 0
    }

    # Text Metrics
    if gt_text is not None and gt_text != "" and pred_text is not None and pred_text != "":
        # Simple Levenshtein distance implementation
        def levenshtein(s1, s2):
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        dist = levenshtein(gt_text, pred_text)
        acc = 1.0 - (dist / max(len(gt_text), len(pred_text), 1))
        
        metrics["char_accuracy"] = max(0.0, acc)
        metrics["edit_distance"] = dist

    # Detection Metrics
    if gt_boxes and len(gt_boxes) > 0:
        matched_gt = set()
        total_iou = 0.0
        tp = 0

        for pred_box in pred_boxes:
            best_iou = 0
            best_gt_idx = -1
            for i, gt_box in enumerate(gt_boxes):
                if i in matched_gt:
                    continue
                iou = compute_iou(pred_box, gt_box)
                if iou > best_iou:
                    best_iou = iou
                    best_gt_idx = i
            
            if best_iou >= iou_threshold:
                tp += 1
                matched_gt.add(best_gt_idx)
                total_iou += best_iou
        
        fp = len(pred_boxes) - tp
        fn = len(gt_boxes) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        metrics["precision"] = precision
        metrics["recall"] = recall
        metrics["hmean"] = f_score
        metrics["iou_average"] = total_iou / tp if tp > 0 else 0.0

    return metrics

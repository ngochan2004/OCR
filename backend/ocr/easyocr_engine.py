"""
EasyOCR Engine for Vietnamese CCCD
Simple, reliable, and accurate OCR solution
"""
import cv2
import numpy as np

# EasyOCR is optional dependency
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Warning: EasyOCR not installed. Run: pip install easyocr")


class EasyOCREngine:
    """
    Wrapper for EasyOCR - simple and effective Vietnamese OCR
    """
    
    def __init__(self, languages=['vi', 'en'], gpu=False):
        """
        Initialize EasyOCR engine
        
        Args:
            languages: List of language codes (default: ['vi', 'en'])
            gpu: Use GPU if available (default: False)
        """
        if not EASYOCR_AVAILABLE:
            raise ImportError("EasyOCR not installed. Run: pip install easyocr")
        
        # Initialize reader (downloads models on first run ~100MB)
        # Use local 'models' directory for storage
        import os
        model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        os.makedirs(model_dir, exist_ok=True)
        
        self.reader = easyocr.Reader(languages, gpu=gpu, model_storage_directory=model_dir, download_enabled=True)
        
    def detect_and_recognize(self, image):
        """
        Run OCR on image using EasyOCR
        
        Args:
            image: numpy array (BGR format from OpenCV)
        
        Returns:
            dict with:
            - boxes: List of [x, y, w, h]
            - texts: List of recognized texts
            - confidences: List of confidence scores
            - full_text: Concatenated text
        """
        # EasyOCR expects RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb = image
        
        # Run EasyOCR
        # Returns: [([[x1,y1], [x2,y2], [x3,y3], [x4,y4]], text, confidence), ...]
        results = self.reader.readtext(rgb)
        
        if not results:
            return {
                'boxes': [],
                'texts': [],
                'confidences': [],
                'full_text': ''
            }
        
        # Parse results
        boxes = []
        texts = []
        confidences = []
        
        for detection in results:
            # detection = (bbox_coords, text, confidence)
            bbox = detection[0]
            text = detection[1]
            conf = detection[2]
            
            # Convert bbox [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] to [x, y, w, h]
            x_coords = [pt[0] for pt in bbox]
            y_coords = [pt[1] for pt in bbox]
            
            x = int(min(x_coords))
            y = int(min(y_coords))
            w = int(max(x_coords) - x)
            h = int(max(y_coords) - y)
            
            boxes.append([x, y, w, h])
            texts.append(text)
            confidences.append(float(conf))
        
        # Sort by y-coordinate (top to bottom), then x (left to right)
        sorted_data = sorted(
            zip(boxes, texts, confidences),
            key=lambda item: (item[0][1], item[0][0])
        )
        
        if sorted_data:
            boxes, texts, confidences = zip(*sorted_data)
            boxes = list(boxes)
            texts = list(texts)
            confidences = list(confidences)
        
        # Join text with newlines
        full_text = '\n'.join(texts)
        
        return {
            'boxes': boxes,
            'texts': texts,
            'confidences': confidences,
            'full_text': full_text
        }

    def recognize_from_boxes(self, image, boxes):
        """
        Recognize text from provided bounding boxes
        
        Args:
            image: numpy array (BGR)
            boxes: List of [x, y, w, h]
            
        Returns:
            dict with boxes, texts, confidences, full_text
        """
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb = image
            
        # Convert [x, y, w, h] to [[x,y], [x+w,y], [x+w,y+h], [x,y+h]]
        horizontal_list = []
        for box in boxes:
            x, y, w, h = box
            points = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
            horizontal_list.append(points)
            
        # Use recognize method if available (bypasses detection)
        # easyocr.Reader.recognize(img, horizontal_list=None, free_list=None, decoder='greedy', beamWidth=5, batch_size=1, workers=0, allowlist=None, blocklist=None, detail=1, rotation_info=None, paragraph=False, min_size=10, contrast_ths=0.1, adjust_contrast=0.5, filter_ths=0.003, text_threshold=0.7, low_text=0.4, link_threshold=0.4, canvas_size=2560, mag_ratio=1.0, slope_ths=0.1, ycenter_ths=0.5, height_ths=0.5, width_ths=0.5, add_margin=0.1, reformat=True, output_format='standard')
        try:
            results = self.reader.recognize(rgb, horizontal_list=horizontal_list, free_list=[])
        except (AttributeError, TypeError) as e:
            print(f"EasyOCR recognize method failed: {e}. Using fallback cropping.")

            # Fallback if recognize is not exposed or different version
            results = []
            for box in boxes:
                x, y, w, h = box
                # Ensure crop is within bounds
                y1, y2 = max(0, y), min(rgb.shape[0], y+h)
                x1, x2 = max(0, x), min(rgb.shape[1], x+w)
                
                crop = rgb[y1:y2, x1:x2]
                
                if crop.size == 0:
                    results.append((None, "", 0.0))
                    continue
                    
                res = self.reader.readtext(crop, detail=1)
                # res is list of (bbox, text, conf)
                if not res:
                    results.append((None, "", 0.0))
                    continue
                    
                # We just take the best one or join them
                text = " ".join([r[1] for r in res])
                conf = np.mean([r[2] for r in res]) if res else 0.0
                results.append((None, text, conf))

        # Parse results
        # recognize returns list of (bbox, text, conf) or similar depending on version
        # standard easyocr recognize returns list of (bbox, text, conf)
        
        out_boxes = []
        out_texts = []
        out_confidences = []
        
        # If we used the fallback loop, results matches the count of boxes
        # If we used reader.recognize, it returns results for each box in order
        
        for i, detection in enumerate(results):
            # detection format might vary, but usually (bbox, text, conf)
            # bbox in recognize output is the same as input usually
            
            text = detection[1]
            conf = detection[2]
            
            # Use original box
            out_boxes.append(boxes[i])
            out_texts.append(text)
            out_confidences.append(float(conf))
            
        full_text = '\n'.join(out_texts)
        
        return {
            'boxes': out_boxes,
            'texts': out_texts,
            'confidences': out_confidences,
            'full_text': full_text
        }


def create_easyocr_engine(languages=['vi', 'en'], gpu=False):
    """
    Factory function to create EasyOCR engine
    
    Args:
        languages: List of language codes
        gpu: Use GPU if available
    
    Returns:
        EasyOCREngine instance or None if not available
    """
    if not EASYOCR_AVAILABLE:
        print("EasyOCR not available. Please install: pip install easyocr")
        return None
    
    try:
        return EasyOCREngine(languages=languages, gpu=gpu)
    except Exception as e:
        print(f"Error initializing EasyOCR: {e}")
        return None


def draw_results(image, boxes, texts, confidences):
    """
    Draw bounding boxes and text on image
    
    Args:
        image: Input image (BGR)
        boxes: List of [x, y, w, h]
        texts: List of text strings
        confidences: List of confidence scores
    
    Returns:
        Image with drawn boxes and text
    """
    viz = image.copy()
    
    for box, text, conf in zip(boxes, texts, confidences):
        x, y, w, h = box
        
        # Draw box (green)
        cv2.rectangle(viz, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw confidence
        label = f"{conf:.2f}"
        cv2.putText(
            viz, label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 255, 0), 1
        )
    
    return viz

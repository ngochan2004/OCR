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
        self.reader = easyocr.Reader(languages, gpu=gpu)
        
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

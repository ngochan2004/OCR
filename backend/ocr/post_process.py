"""
Post-processing module for Vietnamese CCCD (ID Card) OCR
Handles line merging, text cleaning, and structured output
"""
import re
from typing import List, Dict, Tuple

def merge_lines(boxes: List[List[int]], texts: List[str], y_threshold=10, x_gap_threshold=50) -> List[Dict]:
    """
    Merge boxes that belong to the same line.
    
    Args:
        boxes: List of [x, y, w, h]
        texts: List of text strings
        y_threshold: Max vertical difference to consider same line (pixels)
        x_gap_threshold: Max horizontal gap to merge (pixels)
    
    Returns:
        List of dicts with merged 'box', 'text', and 'line_id'
    """
    if not boxes or not texts:
        return []
    
    # Combine boxes and texts
    items = []
    for box, text in zip(boxes, texts):
        x, y, w, h = box
        items.append({
            'box': box,
            'text': text.strip(),
            'x': x,
            'y': y,
            'x2': x + w,
            'y2': y + h,
            'center_y': y + h / 2,
            'w': w,
            'h': h
        })
    
    # Sort by y (top to bottom), then x (left to right)
    items.sort(key=lambda item: (item['y'], item['x']))
    
    # Group into lines
    lines = []
    current_line = []
    
    for item in items:
        if not current_line:
            current_line.append(item)
            continue
        
        # Check if on same line as last item
        last_item = current_line[-1]
        y_diff = abs(item['center_y'] - last_item['center_y'])
        x_gap = item['x'] - last_item['x2']
        
        if y_diff < y_threshold and x_gap < x_gap_threshold:
            # Same line
            current_line.append(item)
        else:
            # New line
            lines.append(current_line)
            current_line = [item]
    
    # Don't forget last line
    if current_line:
        lines.append(current_line)
    
    # Merge text within each line
    merged_results = []
    for line_id, line in enumerate(lines):
        # Sort line items by x coordinate
        line.sort(key=lambda item: item['x'])
        
        # Merge text with spaces
        merged_text = ' '.join([item['text'] for item in line])
        
        # Calculate merged bounding box
        x1 = min(item['x'] for item in line)
        y1 = min(item['y'] for item in line)
        x2 = max(item['x2'] for item in line)
        y2 = max(item['y2'] for item in line)
        
        merged_results.append({
            'box': [x1, y1, x2 - x1, y2 - y1],
            'text': merged_text,
            'line_id': line_id
        })
    
    return merged_results


def clean_cccd_text(text: str) -> str:
    """
    Clean common OCR errors in Vietnamese CCCD text.
    
    Args:
        text: Raw OCR text
    
    Returns:
        Cleaned text
    """
    if not text:
        return text
    
    # Fix "sa." or "So:" -> "Số:"
    text = re.sub(r'\b(sa\.|So:)', 'Số:', text, flags=re.IGNORECASE)
    
    # Fix year typos: 199C -> 1990, 203C -> 2030
    text = re.sub(r'(\d{3})C\b', r'\g<1>0', text)
    
    # Fix common number/letter confusion
    text = re.sub(r'\bO(\d)', r'0\1', text)  # O9 -> 09
    text = re.sub(r'(\d)O\b', r'\g<1>0', text)  # 9O -> 90
    
    # Fix "l" vs "1" in numbers
    text = re.sub(r'\bl(\d)', r'1\1', text)  # l9 -> 19
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text


def filter_noise_boxes(merged_lines: List[Dict]) -> List[Dict]:
    """
    Remove noise boxes (1-2 character fragments that overlap with longer lines).
    
    Args:
        merged_lines: List of merged line dicts
    
    Returns:
        Filtered list
    """
    # Filter out very short text (likely noise) unless it's a label
    labels = ['Số:', 'Nam', 'Nữ']
    
    filtered = []
    for line in merged_lines:
        text = line['text'].strip()
        
        # Keep if:
        # - Length > 3 characters
        # - Is a known label
        # - Contains numbers
        if len(text) > 3 or text in labels or re.search(r'\d', text):
            filtered.append(line)
    
    return filtered


def parse_cccd_structure(lines: List[Dict]) -> Dict:
    """
    Parse CCCD text into structured JSON format.
    
    Args:
        lines: List of merged line dicts with 'text' field
    
    Returns:
        Structured dict with CCCD fields
    """
    result = {
        "title": "",
        "subtitle": "",
        "id_number": "",
        "name": "",
        "date_of_birth": "",
        "gender": "",
        "nationality": "",
        "place_of_origin": "",
        "place_of_residence": "",
        "expiry_date": "",
        "raw_lines": []
    }
    
    for line in lines:
        text = clean_cccd_text(line['text'])
        result['raw_lines'].append(text)
        
        text_upper = text.upper()
        
        # Title
        if 'CĂN CƯỚC CÔNG DÂN' in text_upper or 'CCCD' in text_upper:
            result['title'] = text
        
        # Subtitle
        elif 'ĐỘC LẬP' in text_upper and 'TỰ DO' in text_upper:
            result['subtitle'] = text
        
        # ID Number (12 digits)
        elif 'SỐ:' in text_upper or re.match(r'^\d{12}$', text):
            # Extract 12-digit number
            match = re.search(r'\d{12}', text)
            if match:
                result['id_number'] = match.group(0)
        
        # Name
        elif 'HỌ VÀ TÊN' in text_upper or 'TÊN:' in text_upper:
            # Extract name after label
            name = re.sub(r'.*?(Họ và tên|Tên)[\s:]+', '', text, flags=re.IGNORECASE)
            result['name'] = name.strip()
        
        # Date of Birth
        elif 'NGÀY SINH' in text_upper or 'SINH:' in text_upper:
            # Extract date DD/MM/YYYY
            match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text)
            if match:
                result['date_of_birth'] = match.group(0).replace('-', '/')
        
        # Gender
        elif 'GIỚI TÍNH' in text_upper or text_upper in ['NAM', 'NỮ']:
            if 'NAM' in text_upper:
                result['gender'] = 'Nam'
            elif 'NỮ' in text_upper:
                result['gender'] = 'Nữ'
        
        # Nationality
        elif 'QUỐC TỊCH' in text_upper or 'VIỆT NAM' in text_upper:
            nationality = re.sub(r'.*?Quốc tịch[\s:]+', '', text, flags=re.IGNORECASE)
            if 'VIỆT' in nationality.upper():
                result['nationality'] = 'Việt Nam'
        
        # Place of Origin
        elif 'QUÊ QUÁN' in text_upper:
            place = re.sub(r'.*?Quê quán[\s:]+', '', text, flags=re.IGNORECASE)
            result['place_of_origin'] = place.strip()
        
        # Place of Residence
        elif 'NƠI THƯỜNG TRÚ' in text_upper or 'THƯỜNG TRÚ' in text_upper:
            place = re.sub(r'.*?Nơi thường trú[\s:]+', '', text, flags=re.IGNORECASE)
            result['place_of_residence'] = place.strip()
        
        # Expiry Date
        elif 'GIÁ TRỊ ĐẾN' in text_upper or 'HẾT HẠN' in text_upper:
            match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text)
            if match:
                result['expiry_date'] = match.group(0).replace('-', '/')
    
    return result


def process_cccd_ocr(boxes: List[List[int]], texts: List[str]) -> Dict:
    """
    Complete CCCD post-processing pipeline.
    
    Args:
        boxes: List of bounding boxes [x, y, w, h]
        texts: List of OCR text strings
    
    Returns:
        Dict with:
        - 'structured': Parsed CCCD data
        - 'merged_lines': List of merged line dicts
        - 'full_text': Concatenated clean text
    """
    # Step 1: Merge lines
    merged = merge_lines(boxes, texts, y_threshold=15, x_gap_threshold=60)
    
    # Step 2: Filter noise
    filtered = filter_noise_boxes(merged)
    
    # Step 3: Parse structure
    structured = parse_cccd_structure(filtered)
    
    # Step 4: Generate full text
    full_text = '\n'.join([clean_cccd_text(line['text']) for line in filtered])
    
    return {
        'structured': structured,
        'merged_lines': filtered,
        'full_text': full_text
    }

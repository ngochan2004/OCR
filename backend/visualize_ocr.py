import cv2
import easyocr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys
import os

def visualize_ocr(image_path, output_path='result_vis.jpg'):
    """
    Visualize EasyOCR results with Red Box + White Text on Red Background.
    Supports Vietnamese characters using PIL.
    """
    
    # 1. Check input file
    if not os.path.exists(image_path):
        print(f"❌ Error: File not found: {image_path}")
        return

    print(f"🚀 Processing: {image_path}")
    
    # 2. Initialize EasyOCR (Vietnamese + English)
    # gpu=True if you have CUDA, else False
    try:
        reader = easyocr.Reader(['vi', 'en'], gpu=False) 
    except Exception as e:
        print(f"❌ Error initializing EasyOCR: {e}")
        return

    # 3. Read Image
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Error: Cannot read image with OpenCV")
        return

    # 4. Run OCR
    print("🔍 Running text detection...")
    results = reader.readtext(img)
    print(f"✅ Found {len(results)} text regions")

    # 5. Visualization (Using PIL for Unicode support)
    # Convert BGR (OpenCV) to RGB (PIL)
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # Load Font (Arial for Vietnamese support)
    font_size = 24
    try:
        # Try common Windows font paths
        font_path = "C:/Windows/Fonts/arial.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf" # Try current dir
        
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("⚠️ Warning: Arial font not found. Using default (Vietnamese may display incorrectly).")
        font = ImageFont.load_default()

    for (bbox, text, prob) in results:
        # bbox format: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1])) # Top-Left
        br = (int(br[0]), int(br[1])) # Bottom-Right

        # --- A. Draw Bounding Box (Red) ---
        draw.rectangle([tl, br], outline="red", width=3)

        # --- B. Draw Text with Red Background ---
        # Calculate text size
        if hasattr(draw, 'textbbox'):
            # Pillow >= 9.2.0
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_w, text_h = right - left, bottom - top
        else:
            # Older Pillow
            text_w, text_h = draw.textsize(text, font=font)

        # Position: Above the box
        text_x = tl[0]
        text_y = tl[1] - text_h - 10
        
        # If text goes off top edge, put it below the box
        if text_y < 0:
            text_y = br[1] + 5

        # Draw Red Background Rectangle
        padding = 5
        draw.rectangle(
            [
                (text_x, text_y), 
                (text_x + text_w + padding*2, text_y + text_h + padding*2)
            ],
            fill="red"
        )

        # Draw White Text
        draw.text(
            (text_x + padding, text_y + padding), 
            text, 
            font=font, 
            fill="white"
        )

    # 6. Save Result
    img_pil.save(output_path)
    print(f"💾 Saved result to: {output_path}")

    # 7. Show Result (using OpenCV window)
    # Convert RGB (PIL) back to BGR (OpenCV)
    result_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    # Resize if too big for screen
    h, w = result_cv.shape[:2]
    if h > 1000:
        scale = 1000 / h
        result_cv = cv2.resize(result_cv, (0, 0), fx=scale, fy=scale)
    
    cv2.imshow("EasyOCR Result (Press any key to exit)", result_cv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        img_file = sys.argv[1]
        visualize_ocr(img_file)
    else:
        print("\nUsage: python visualize_ocr.py <path_to_image>")
        print("Example: python visualize_ocr.py cccd_sample.jpg")
        
        # Auto-find first image in current dir for convenience
        exts = ('.jpg', '.jpeg', '.png', '.bmp')
        files = [f for f in os.listdir('.') if f.lower().endswith(exts)]
        if files:
            print(f"\nFound image '{files[0]}', processing automatically...")
            visualize_ocr(files[0])

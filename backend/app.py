from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2
import time
import os
import json
from ocr import evaluator

# Import EasyOCR engine
try:
    from ocr.easyocr_engine import create_easyocr_engine, draw_results
    from ocr.post_process import process_cccd_ocr
    EASYOCR_AVAILABLE = True
    _easyocr_engine_cache = None
except ImportError as e:
    EASYOCR_AVAILABLE = False
    print(f"EasyOCR not available: {e}")

app = FastAPI(title="OCR API with EasyOCR")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def root():
    return {
        "message": "OCR API ready", 
        "version": "4.0 - EasyOCR",
        "engine": "EasyOCR",
        "easyocr_available": EASYOCR_AVAILABLE
    }

@app.post("/ocr")
async def ocr(
    file: UploadFile = File(...), 
    gt_text: str = Form(None), 
    gt_boxes: str = Form(None),
    lang: str = Form("vi"),  # Default to Vietnamese
    structured: bool = Form(True)
):
    global _easyocr_engine_cache
    start_time = time.perf_counter()
    
    if not EASYOCR_AVAILABLE:
        return JSONResponse(
            status_code=500, 
            content={"error": "EasyOCR not installed. Run: pip install easyocr"}
        )
    
    # Map frontend language codes to EasyOCR codes
    # vie -> vi, eng -> en
    lang_map = {
        "vie": "vi",
        "eng": "en",
        "vie+eng": ["vi", "en"]
    }
    
    target_langs = lang_map.get(lang, ["vi", "en"])
    if isinstance(target_langs, str):
        target_langs = [target_langs]
        
    # Ensure English is always included for better number/symbol detection
    if "en" not in target_langs:
        target_langs.append("en")

    # Read image
    data = await file.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "Cannot read image"})

    # Initialize EasyOCR with requested languages
    # Note: EasyOCR caches models, so re-initializing is relatively cheap if models are downloaded
    print(f"Initializing EasyOCR with languages: {target_langs}")
    try:
        # We create a new instance or update the existing one if languages changed
        # For simplicity in this demo, we'll just get/create the engine
        # In production, you might want a pool of readers for different langs
        engine = create_easyocr_engine(languages=target_langs, gpu=False)
        
        if engine is None:
            return JSONResponse(status_code=500, content={"error": "EasyOCR initialization failed"})
            
        # Run OCR
        ocr_result = engine.detect_and_recognize(img)
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    # Apply post-processing if requested
    cccd_data = None
    if structured and ocr_result['boxes']:
        processed = process_cccd_ocr(ocr_result['boxes'], ocr_result['texts'])
        cccd_data = processed['structured']
        full_text = processed['full_text']
        results = processed['merged_lines']
    else:
        # Use raw results
        results = []
        for box, text in zip(ocr_result['boxes'], ocr_result['texts']):
            results.append({"box": box, "text": text})
        full_text = ocr_result['full_text']
    
    # Draw visualization
    viz_img = draw_results(
        img, 
        ocr_result['boxes'],
        ocr_result['texts'],
        ocr_result['confidences']
    )
    
    # Export files
    import uuid
    # Use UUID to avoid unicode filename issues on Windows
    safe_filename = str(uuid.uuid4())
    output_text_path = os.path.join(OUTPUT_DIR, f"{safe_filename}.txt")
    output_img_path = os.path.join(OUTPUT_DIR, f"{safe_filename}_boxed.png")
    output_metrics_path = os.path.join(OUTPUT_DIR, f"{safe_filename}_metrics.json")
    
    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    # cv2.imwrite doesn't support unicode paths on Windows, but UUID is safe ASCII
    cv2.imwrite(output_img_path, viz_img)

    # Metrics
    metrics = {}
    parsed_gt_boxes = None
    if gt_boxes:
        try:
            parsed_gt_boxes = json.loads(gt_boxes)
        except:
            pass
            
    if gt_text or parsed_gt_boxes:
        metrics = evaluator.evaluate_metrics(
            parsed_gt_boxes if parsed_gt_boxes else [], 
            [r["box"] for r in results], 
            gt_text, 
            " ".join([r["text"] for r in results])
        )

    # Layout Summary
    img_area = img.shape[0] * img.shape[1]
    text_area = sum([box[2] * box[3] for box in ocr_result['boxes']])
    text_density = (text_area / img_area) * 100 if img_area > 0 else 0
    
    layout_summary = {
        "num_text_boxes": len(ocr_result['boxes']),
        "text_density_percent": round(text_density, 2),
        "avg_box_size": round(text_area / len(ocr_result['boxes']), 2) if len(ocr_result['boxes']) > 0 else 0,
        "image_dimensions": {"width": img.shape[1], "height": img.shape[0]}
    }

    # Export metrics
    metrics_output = {
        "metrics": metrics,
        "layout_summary": layout_summary,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "engine": "EasyOCR"
    }
    
    with open(output_metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_output, f, indent=2)

    latency = time.perf_counter() - start_time

    response = {
        "boxes": results,
        "text": full_text,
        "latency": latency,
        "metrics": metrics,
        "layout_summary": layout_summary,
        "engine": "EasyOCR",
        "image_size": {"w": img.shape[1], "h": img.shape[0]},
        "output_files": {
            "text": output_text_path,
            "image": output_img_path,
            "metrics": output_metrics_path
        }
    }
    
    # Add CCCD structured data if available
    if cccd_data:
        response["cccd"] = cccd_data
    
    return response

# Mount static files
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

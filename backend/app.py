from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import pytesseract
import time

# Khai báo đường dẫn Tesseract nếu cần (Windows)
# Nếu bạn cài ở C:\Program Files\Tesseract-OCR\tesseract.exe thì thêm dòng này:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip().replace("\n", " ").replace("\r", " ")

def char_accuracy(gt: str, pred: str):
    import difflib
    seq = difflib.SequenceMatcher(None, gt, pred)
    acc = seq.ratio()
    dist = len(gt) + len(pred) - 2 * int(acc * min(len(gt), len(pred)))
    return acc, dist

app = FastAPI(title="OCR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "OCR API ready"}

@app.post("/ocr")
async def ocr(file: UploadFile = File(...), gt_text: str = Form(None), lang: str = Form("eng")):
    data = await file.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "cannot read image"})

    # Dùng pytesseract để lấy text + bounding box
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

    results, texts = [], []
    for i in range(len(data['text'])):
        if data['text'][i].strip() != "":
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            txt = clean_text(data['text'][i])
            results.append({"box": [x, y, w, h], "text": txt})
            texts.append(txt)

    full_text = clean_text(" ".join(texts))
    latency = time.perf_counter()

    metrics = {}
    if gt_text:
        acc, dist = char_accuracy(gt_text, full_text)
        metrics = {"char_accuracy": acc, "edit_distance": dist}

    return {
        "boxes": results,
        "text": full_text,
        "latency": latency,
        "metrics": metrics,
        "image_size": {"w": img.shape[1], "h": img.shape[0]}  # gửi thêm kích thước ảnh gốc
    }

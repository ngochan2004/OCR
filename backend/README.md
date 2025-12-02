# 🇻🇳 Vietnamese CCCD OCR System

A high-accuracy OCR system specialized for Vietnamese Identity Cards (CCCD), powered by EasyOCR and custom post-processing.

## 🚀 Features

-   **High Accuracy:** Uses EasyOCR deep learning models optimized for Vietnamese.
-   **Smart Post-Processing:**
    -   **Line Merging:** Automatically joins fragmented words into complete sentences.
    -   **Typo Fixer:** Corrects common OCR errors (e.g., `199C` -> `1990`).
    -   **Structure Parsing:** Extracts key fields (Name, ID, DOB) into JSON format.
-   **Dual Language Support:** Handles mixed Vietnamese and English content.
-   **Visualization:** Generates debug images with bounding boxes and confidence scores.

## 🛠️ Installation

1.  **Prerequisites:**
    -   Python 3.8+
    -   Node.js (for Frontend)

2.  **Backend Setup:**
    ```bash
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    # Or manually: pip install fastapi uvicorn python-multipart opencv-python easyocr
    ```

3.  **Frontend Setup:**
    ```bash
    cd frontend
    npm install
    ```

## 🏃 Usage

1.  **Start Backend:**
    ```bash
    cd backend
    uvicorn app:app --reload
    ```
    *Note: First run will download EasyOCR models (~100MB).*

2.  **Start Frontend:**
    ```bash
    cd frontend
    npm run dev
    ```

3.  **Access:** Open `http://localhost:5173`

## 📂 Project Structure

```
backend/
├── app.py                 # Main API Server (FastAPI)
├── ocr/
│   ├── easyocr_engine.py  # EasyOCR Wrapper
│   ├── post_process.py    # Merging & Cleaning Logic
│   └── evaluator.py       # Metrics Calculation
├── outputs/               # Debug images & results
└── visualize_ocr.py       # Standalone debug script
```

## 🔍 API Endpoint

**POST** `/ocr`

**Parameters:**
-   `file`: Image file (binary)
-   `lang`: `vie` (default), `eng`, or `vie+eng`
-   `structured`: `true` (default) - Enable CCCD parsing

**Response:**
```json
{
  "text": "Full extracted text...",
  "cccd": {
    "id_number": "079090000555",
    "name": "NGUYỄN VĂN A",
    "date_of_birth": "01/01/1990",
    ...
  },
  "boxes": [...]
}
```

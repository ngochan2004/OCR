# 🧠 OCR Algorithm & Logic Explanation

This document explains the core algorithms used in the Vietnamese CCCD OCR system.

## 1. Core Engine: EasyOCR
We use **EasyOCR** as the unified engine for both text detection and recognition.

### A. Text Detection: CRAFT (ICDAR2015 Compliant)
-   **Model:** EasyOCR uses the **CRAFT (Character Region Awareness for Text Detection)** algorithm.
-   **Performance:** CRAFT is a state-of-the-art scene text detector trained on **ICDAR2015** and other datasets. It is highly effective at detecting text of varying sizes, orientations, and shapes.
-   **Why CRAFT?** It outperforms standard EAST implementations in many complex scenarios, especially for curved or irregular text.

### B. Text Recognition: CRNN
-   **Model:** CRNN/ResNet based architecture.
-   **Why EasyOCR?**
    -   It has built-in support for **Vietnamese** (handling accents/diacritics much better than Tesseract).
    -   It is robust against noisy backgrounds.
-   **Configuration:**
    -   `languages=['vi', 'en']`: We load both Vietnamese and English models.
    -   `gpu=False`: Configured for CPU usage.

## 2. Post-Processing Pipeline (`ocr/post_process.py`)
Raw OCR output is often fragmented (e.g., "CỘNG" "HÒA" "XÃ" "HỘI" as separate boxes). We implement a custom pipeline to fix this.

### A. Line Merging Algorithm
**Goal:** Combine fragmented words into complete lines (e.g., "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM").

**Logic:**
1.  **Sort Boxes:** First by Y-coordinate (top-to-bottom), then by X-coordinate (left-to-right).
2.  **Iterate & Group:**
    -   We compare the current box with the last box in the current line.
    -   **Vertical Check:** If `abs(y_center1 - y_center2) < 15px`, they are on the same line.
    -   **Horizontal Check:** If `x_gap < 60px`, they are close enough to be part of the same sentence.
    -   **Merge:** If both conditions are met, we group them.
3.  **Result:** A list of merged lines with updated bounding boxes.

### B. Text Cleaning (Regex)
**Goal:** Fix common OCR errors specific to Vietnamese CCCD.

-   **Label Correction:**
    -   `sa.` or `So:` $\rightarrow$ `Số:`
-   **Number/Letter Confusion:**
    -   `199C` $\rightarrow$ `1990` (Common error where '0' is read as 'C')
    -   `O9` $\rightarrow$ `09` (Letter 'O' read as number '0')
    -   `l9` $\rightarrow$ `19` (Letter 'l' read as number '1')

### C. Structured Parsing
**Goal:** Extract specific fields (Name, ID, DOB) from the unstructured text lines.

We iterate through the merged lines and look for keywords:
-   **ID Number:** Look for 12-digit patterns (`^\d{12}$`) or lines containing "Số:".
-   **Name:** Look for lines after "Họ và tên" or "Tên".
-   **DOB:** Look for date patterns (`DD/MM/YYYY`) near "Ngày sinh".
-   **Expiry:** Look for date patterns near "Có giá trị đến".

## 3. Architecture Overview

```mermaid
graph TD
    A[Input Image] --> B[EasyOCR (CRAFT Detector)]
    B --> C[Text Boxes]
    C --> D[EasyOCR (CRNN Recognizer)]
    D --> E{Raw Output}
    E --> F[Line Merging]
    D --> E[Noise Filtering]
    E --> F[Text Cleaning]
    F --> G[Structure Parser]
    G --> H[Final JSON Output]
```

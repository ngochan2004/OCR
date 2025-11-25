import React, { useState, useRef, useEffect } from "react";
import { runOCR } from "../api";

export default function OCRForm() {
    const [file, setFile] = useState(null);
    const [gt, setGt] = useState("");
    const [lang, setLang] = useState("eng");
    const [ocr, setOcr] = useState(null);
    const imgRef = useRef(null);

    const handleOCR = async () => {
        if (!file) return;
        const res = await runOCR(file, gt, lang);
        setOcr(res);
    };

    const handleDownload = () => {
        if (!ocr) return;
        const content = `
OCR Result
==========

Text:
${ocr.text}

Latency: ${ocr.latency?.toFixed(3)}s

Metrics:
- Char Accuracy: ${ocr.metrics?.char_accuracy ?? "N/A"}
- Edit Distance: ${ocr.metrics?.edit_distance ?? "N/A"}
        `;
        const blob = new Blob([content], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "ocr_result.txt";
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <section id="ocr" className="mt-16">
            <div className="card space-y-4 animate-fade-in">
                <h2 className="subtitle">Nhập ảnh để nhận diện văn bản</h2>

                {/* Custom file input */}
                <label className="block">
                    <span className="text-sm font-medium text-gray-700">Chọn ảnh 📁</span>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => setFile(e.target.files[0])}
                    />
                </label>

                <textarea
                    className="input"
                    placeholder="Ground Truth (tùy chọn)"
                    value={gt}
                    onChange={(e) => setGt(e.target.value)}
                />

                <select
                    className="input"
                    value={lang}
                    onChange={(e) => setLang(e.target.value)}
                >
                    <option value="eng">English</option>
                    <option value="vie">Tiếng Việt</option>
                </select>

                <button className="btn" onClick={handleOCR}>
                    Nhận diện văn bản
                </button>
            </div>

            {/* Kết quả OCR */}
            {ocr && (
                <div className="card mt-8 animate-slide-up">
                    <h2 className="subtitle">Kết quả OCR</h2>
                    <p><b>Text:</b> {ocr.text}</p>
                    <p><b>Latency:</b> {ocr.latency?.toFixed(3)}s</p>
                    {ocr.metrics && (
                        <div className="mt-2">
                            <p><b>Độ chính xác ký tự:</b> {ocr.metrics.char_accuracy}</p>
                            <p><b>Edit distance:</b> {ocr.metrics.edit_distance}</p>
                        </div>
                    )}
                    <button className="btn mt-4" onClick={handleDownload}>
                        📥 Tải xuống kết quả (.txt)
                    </button>
                </div>
            )}

            {/* Ảnh với bounding boxes */}
            {file && ocr && (
                <div className="card mt-8 animate-zoom-in">
                    <h2 className="subtitle">Ảnh với bounding boxes</h2>
                    <div className="ocr-image-container" style={{ position: "relative", maxWidth: "600px" }}>
                        <img
                            ref={imgRef}
                            src={URL.createObjectURL(file)}
                            alt="Uploaded"
                            className="rounded shadow-lg"
                            style={{ width: "100%", height: "auto", display: "block" }}
                        />
                        {ocr.boxes && ocr.boxes.map((b, i) => {
                            const [x, y, w, h] = b.box;
                            const displayedWidth = 600; // khớp với maxWidth
                            const scaleX = displayedWidth / ocr.image_size.w;
                            const scaleY = displayedWidth / ocr.image_size.w; // giữ tỉ lệ theo width

                            return (
                                <div
                                    key={i}
                                    className="ocr-box"
                                    style={{
                                        position: "absolute",
                                        border: "2px solid red",
                                        left: x * scaleX,
                                        top: y * scaleY,
                                        width: w * scaleX,
                                        height: h * scaleY,
                                        boxSizing: "border-box",
                                        pointerEvents: "none"
                                    }}
                                >
                                    <span
                                        className="ocr-text"
                                        style={{
                                            position: "absolute",
                                            top: "-1.2rem",
                                            left: 0,
                                            background: "rgba(255,0,0,0.8)",
                                            color: "#fff",
                                            fontSize: "0.75rem",
                                            padding: "2px 4px",
                                            borderRadius: "3px",
                                            whiteSpace: "nowrap"
                                        }}
                                    >
                                        {b.text}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </section>
    );
}

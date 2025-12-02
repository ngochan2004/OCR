import React, { useState } from "react";
import { runOCR } from "../api";

export default function OCRForm() {
    const [file, setFile] = useState(null);
    const [gt, setGt] = useState("");
    const [lang, setLang] = useState("vie");
    const [ocr, setOcr] = useState(null);
    const [loading, setLoading] = useState(false);
    const [boxedImage, setBoxedImage] = useState(null);

    const handleOCR = async () => {
        if (!file) return;
        setLoading(true);
        try {
            const res = await runOCR(file, gt, lang);
            setOcr(res);

            if (res.output_files && res.output_files.image) {
                // Backend returns full path like "outputs/uuid_boxed.png"
                // We need to convert it to URL: http://localhost:8000/outputs/uuid_boxed.png
                // Note: The backend path might use backslashes on Windows, so we replace them
                const imagePath = res.output_files.image.replace(/\\/g, '/').split('/').pop();
                const boxedUrl = `http://localhost:8000/outputs/${imagePath}?t=${Date.now()}`;
                setBoxedImage(boxedUrl);
            }
        } catch (error) {
            console.error("OCR Error:", error);
            alert("Lỗi khi xử lý OCR. Vui lòng thử lại.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <section id="ocr" className="mt-16">
            <div className="card space-y-4 animate-fade-in">
                <h2 className="subtitle">Nhập ảnh để nhận diện văn bản</h2>

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
                    placeholder="Ground Truth (tùy chọn) - Nhập văn bản chuẩn để tính toán Metrics ICDAR 2015"
                    value={gt}
                    onChange={(e) => setGt(e.target.value)}
                />

                <select
                    className="input"
                    value={lang}
                    onChange={(e) => setLang(e.target.value)}
                >
                    <option value="vie">Tiếng Việt</option>
                    <option value="eng">English</option>
                    <option value="vie+eng">Tiếng Việt + English</option>
                </select>

                <button
                    className="btn"
                    onClick={handleOCR}
                    disabled={!file || loading}
                >
                    {loading ? "Đang xử lý..." : "🔍 Nhận diện văn bản"}
                </button>
            </div>

            {/* Ảnh với bounding boxes */}
            {boxedImage && (
                <div className="card mt-8 animate-zoom-in">
                    <h2 className="subtitle">📸 Ảnh với Bounding Boxes</h2>
                    <div className="border rounded-lg overflow-hidden shadow-lg">
                        <img
                            src={boxedImage}
                            alt="OCR Result with Boxes"
                            className="w-full h-auto"
                            onError={(e) => console.error("Failed to load boxed image:", e)}
                        />
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                        ✓ Đã vẽ {ocr?.boxes?.length ?? 0} vùng text
                    </p>
                </div>
            )}

            {/* Nội dung văn bản */}
            {ocr && (
                <div className="card mt-8 animate-slide-up">
                    <h2 className="subtitle">📝 Nội dung văn bản</h2>
                    <div className="bg-gray-50 p-4 rounded border border-gray-200">
                        <pre className="whitespace-pre-wrap font-mono text-sm">
                            {ocr.text || "(Không phát hiện văn bản)"}
                        </pre>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                        ⏱️ Thời gian xử lý: {ocr.latency?.toFixed(3)}s
                    </p>
                </div>
            )}

            {/* ICDAR 2015 Metrics - ALWAYS SHOW */}
            {ocr?.metrics && (
                <div className="card mt-8 animate-fade-in">
                    <h2 className="subtitle">📊 ICDAR 2015 Metrics</h2>

                    {(!ocr.metrics.precision && !ocr.metrics.char_accuracy) ? (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <p className="text-sm text-yellow-800">
                                ℹ️ <strong>Chưa có metrics</strong> - Nhập <strong>Ground Truth</strong> (văn bản chuẩn) vào ô trên để tính toán độ chính xác theo chuẩn ICDAR 2015
                            </p>
                            <p className="text-xs text-yellow-700 mt-2">
                                💡 Metrics gồm: Precision, Recall, F-score (Detection) + Character Accuracy, Edit Distance (Recognition)
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Detection Metrics */}
                            {(ocr.metrics.precision > 0 || ocr.metrics.recall > 0) && (
                                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                                    <h3 className="font-semibold text-blue-900 mb-3">Detection Metrics</h3>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span>Precision:</span>
                                            <span className="font-mono font-bold text-blue-600">
                                                {(ocr.metrics.precision * 100).toFixed(2)}%
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Recall:</span>
                                            <span className="font-mono font-bold text-blue-600">
                                                {(ocr.metrics.recall * 100).toFixed(2)}%
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>F-score:</span>
                                            <span className="font-mono font-bold text-green-600">
                                                {(ocr.metrics.hmean * 100).toFixed(2)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Recognition Metrics */}
                            {(ocr.metrics.char_accuracy > 0) && (
                                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                    <h3 className="font-semibold text-green-900 mb-3">Recognition Metrics</h3>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span>Character Accuracy:</span>
                                            <span className="font-mono font-bold text-green-600">
                                                {(ocr.metrics.char_accuracy * 100).toFixed(2)}%
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span>Edit Distance:</span>
                                            <span className="font-mono font-bold text-orange-600">
                                                {ocr.metrics.edit_distance}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Layout Summary */}
            {ocr?.layout_summary && (
                <div className="card mt-8">
                    <h2 className="subtitle">📐 Layout Summary</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-purple-50 p-4 rounded-lg border text-center">
                            <div className="text-3xl font-bold text-purple-600">
                                {ocr.layout_summary.num_text_boxes}
                            </div>
                            <div className="text-sm text-gray-600 mt-1">Text Boxes</div>
                        </div>
                        <div className="bg-pink-50 p-4 rounded-lg border text-center">
                            <div className="text-3xl font-bold text-pink-600">
                                {ocr.layout_summary.text_density_percent.toFixed(1)}%
                            </div>
                            <div className="text-sm text-gray-600 mt-1">Density</div>
                        </div>
                        <div className="bg-indigo-50 p-4 rounded-lg border text-center">
                            <div className="text-2xl font-bold text-indigo-600">
                                {ocr.layout_summary.avg_box_size.toFixed(0)}px
                            </div>
                            <div className="text-sm text-gray-600 mt-1">Avg Size</div>
                        </div>
                        <div className="bg-teal-50 p-4 rounded-lg border text-center">
                            <div className="text-xl font-bold text-teal-600">
                                {ocr.layout_summary.image_dimensions.width}×{ocr.layout_summary.image_dimensions.height}
                            </div>
                            <div className="text-sm text-gray-600 mt-1">Image Size</div>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}

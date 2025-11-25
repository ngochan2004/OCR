import React from "react";

export default function Guide() {
    const steps = [
        "Chọn ảnh chứa văn bản (hóa đơn, sách, bảng hiệu...).",
        "Chọn ngôn ngữ phù hợp.",
        "Nhấn 'Nhận diện văn bản'.",
        "Xem kết quả OCR và tải xuống file .txt."
    ];
    return (
        <section className="card mt-12">
            <h2 className="subtitle">📚 Hướng dẫn sử dụng</h2>
            <ul className="list-disc pl-6 text-gray-700">
                {steps.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
        </section>
    );
}

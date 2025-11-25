import React from "react";

export default function FAQ() {
    const faqs = [
        { q: "OCR có chính xác không?", a: "Độ chính xác phụ thuộc vào chất lượng ảnh và ngôn ngữ." },
        { q: "Hỗ trợ ngôn ngữ nào?", a: "Tiếng Anh, Tiếng Việt, và nhiều ngôn ngữ khác qua Tesseract." },
        { q: "Ảnh của tôi có được lưu không?", a: "Không, ảnh chỉ xử lý cục bộ và không lưu trữ." }
    ];
    return (
        <section className="card mt-12">
            <h2 className="subtitle">❓ Câu hỏi thường gặp</h2>
            {faqs.map((f, i) => (
                <div key={i} className="mb-4">
                    <p className="font-semibold">{f.q}</p>
                    <p className="text-gray-600">{f.a}</p>
                </div>
            ))}
        </section>
    );
}

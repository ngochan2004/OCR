import React from "react";

export default function Comparison() {
    return (
        <section className="card mt-12">
            <h2 className="subtitle">🔍 So sánh trước / sau OCR</h2>
            <div className="grid md:grid-cols-2 gap-6">
                <div>
                    <h3 className="font-semibold">Ảnh gốc</h3>
                    <img src="/example_invoice.png" alt="Ảnh gốc" className="rounded shadow" />
                </div>
                <div>
                    <h3 className="font-semibold">Kết quả OCR</h3>
                    <pre className="bg-gray-100 p-4 rounded">Invoice #12345\nDate: 25/11/2025\nTotal: $250</pre>
                </div>
            </div>
        </section>
    );
}

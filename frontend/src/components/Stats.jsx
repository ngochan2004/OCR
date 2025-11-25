import React from "react";

export default function Stats() {
    return (
        <section className="card mt-12">
            <h2 className="subtitle">📊 Thống kê hiệu suất</h2>
            <ul className="list-disc pl-6 text-gray-700">
                <li>Tốc độ xử lý trung bình: 0.8s / ảnh</li>
                <li>Độ chính xác ký tự: ~95%</li>
                <li>Ngôn ngữ hỗ trợ: 100+ ngôn ngữ</li>
            </ul>
        </section>
    );
}

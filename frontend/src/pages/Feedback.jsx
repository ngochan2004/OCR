import React, { useState } from "react";

export default function Feedback() {
    const [text, setText] = useState("");
    const [rating, setRating] = useState(5);

    return (
        <section className="card space-y-4">
            <h2 className="subtitle">Góp ý & Đánh giá</h2>
            <textarea
                className="input"
                placeholder="Bạn có góp ý gì không?"
                value={text}
                onChange={(e) => setText(e.target.value)}
            />
            <label className="block text-sm font-medium text-gray-700">Đánh giá:</label>
            <select
                className="input w-32"
                value={rating}
                onChange={(e) => setRating(e.target.value)}
            >
                {[5, 4, 3, 2, 1].map((r) => (
                    <option key={r} value={r}>{r} sao</option>
                ))}
            </select>
            <button className="btn">Gửi góp ý</button>
        </section>
    );
}

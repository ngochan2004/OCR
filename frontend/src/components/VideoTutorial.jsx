import React from "react";

export default function VideoTutorial() {
    return (
        <section className="card mt-12">
            <h2 className="subtitle">🎥 Video hướng dẫn</h2>
            <p className="text-gray-600 mb-4">Xem video để biết cách sử dụng OCR Web trong thực tế:</p>
            <iframe
                className="w-full h-64 rounded shadow"
                src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                title="Video hướng dẫn OCR Web"
                allowFullScreen
            ></iframe>
        </section>
    );
}

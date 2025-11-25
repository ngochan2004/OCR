import React from "react";

export default function Contact() {
    return (
        <section className="card space-y-4">
            <h2 className="subtitle">Liên hệ</h2>
            <p className="text-gray-600">Email: <b>yourmail@example.com</b></p>
            <p className="text-gray-600">GitHub: <a href="https://github.com/" className="text-indigo-600 hover:underline">Repo</a></p>
        </section>
    );
}

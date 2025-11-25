import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
    return (
        <footer className="bg-gray-100 border-t border-gray-200 mt-12">
            <div className="max-w-6xl mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between text-sm text-gray-600">
                <p>© 2025 Ngọc | OCR Web</p>
                <div className="flex space-x-4 mt-2 md:mt-0">
                    <a href="https://github.com/" target="_blank" rel="noopener noreferrer" className="hover:text-indigo-600 transition">GitHub</a>
                    <Link to="/contact" className="hover:text-indigo-600 transition">Liên hệ</Link>
                    <Link to="/policy" className="hover:text-indigo-600 transition">Chính sách</Link>
                </div>
            </div>
        </footer>
    );
}

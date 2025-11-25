import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <nav className="bg-white shadow-md sticky top-0 z-50">
            <div className="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
                <h1 className="text-xl font-bold text-indigo-600">OCR Web</h1>
                <ul className="flex space-x-6 text-sm text-gray-700 font-medium">
                    <li><Link to="/">Trang chủ</Link></li>
                    <li><Link to="/feedback">Góp ý</Link></li>
                    <li><Link to="/contact">Liên hệ</Link></li>
                    <li><Link to="/policy">Chính sách</Link></li>
                </ul>
            </div>
        </nav>
    );
}

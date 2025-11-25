import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Feedback from "./pages/Feedback";
import Contact from "./pages/Contact";
import Policy from "./pages/Policy";

export default function App() {
    return (
        <Router>
            <div className="min-h-screen bg-gray-50 flex flex-col">
                <Navbar />
                <main className="flex-grow container py-8">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/feedback" element={<Feedback />} />
                        <Route path="/contact" element={<Contact />} />
                        <Route path="/policy" element={<Policy />} />
                    </Routes>
                </main>
                <Footer />
            </div>
        </Router>
    );
}

import React from "react";

export default function InfoCards() {
    const cards = [
        {
            title: "📄 Ứng dụng dùng để làm gì?",
            desc: "OCR Web giúp bạn trích xuất văn bản từ ảnh chụp tài liệu, hóa đơn, bảng hiệu, sách báo... Ứng dụng này đặc biệt hữu ích cho sinh viên, nhân viên văn phòng, kế toán, hoặc bất kỳ ai cần số hóa tài liệu giấy thành văn bản điện tử để dễ dàng lưu trữ, tìm kiếm và chỉnh sửa.",
        },
        {
            title: "🚀 Lợi ích khi sử dụng",
            desc: "Tiết kiệm thời gian nhập liệu thủ công, giảm sai sót khi gõ lại văn bản. Hỗ trợ số hóa tài liệu để dễ dàng chia sẻ qua email hoặc lưu trữ trên cloud. Giúp doanh nghiệp tăng hiệu quả làm việc, giảm chi phí nhân sự cho công việc nhập liệu.",
        },
        {
            title: "🧠 Công nghệ sử dụng",
            desc: "Ứng dụng này kết hợp FastAPI (backend) để xử lý yêu cầu nhanh chóng, Tesseract OCR để nhận diện văn bản với nhiều ngôn ngữ, và React + TailwindCSS để xây dựng giao diện hiện đại, thân thiện với người dùng. Hệ thống có thể mở rộng để tích hợp thêm AI nâng cao như nhận diện chữ viết tay.",
        },
        {
            title: "📚 Cách sử dụng OCR Web",
            desc: "Chọn ảnh chứa văn bản cần nhận diện, chọn ngôn ngữ phù hợp, sau đó nhấn 'Nhận diện văn bản'. Kết quả sẽ hiển thị bên dưới, kèm theo độ chính xác và thời gian xử lý. Bạn có thể tải kết quả về dưới dạng file .txt.",
        },
        {
            title: "🌐 Hỗ trợ ngôn ngữ",
            desc: "OCR Web hỗ trợ nhiều ngôn ngữ như tiếng Anh, tiếng Việt, tiếng Pháp, tiếng Trung... Bạn có thể mở rộng thêm bằng cách cài thêm dữ liệu ngôn ngữ cho Tesseract.",
        },
        {
            title: "🔒 Bảo mật dữ liệu",
            desc: "Ảnh bạn tải lên chỉ được xử lý cục bộ và không lưu trữ trên máy chủ. OCR Web đảm bảo quyền riêng tư và bảo mật thông tin người dùng.",
        }
    ];

    return (
        <section className="grid md:grid-cols-3 gap-6 mt-12">
            {cards.map((c, i) => (
                <div key={i} className="card hover:shadow-lg transition duration-300 hover:scale-105">
                    <h3 className="text-lg font-semibold mb-2">{c.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{c.desc}</p>
                </div>
            ))}
        </section>
    );
}

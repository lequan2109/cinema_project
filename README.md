🎬 Cinema Pro – Hệ thống Đặt Vé & Phân Tích Dữ Liệu Rạp Chiếu Phim

Cinema Pro là nền tảng quản lý rạp chiếu phim toàn diện được xây dựng bằng Django Framework.
Hệ thống tích hợp quy trình đặt vé real-time, thanh toán điện tử VNPAY, và đặc biệt là Dashboard phân tích dữ liệu chuyên sâu dành cho quản trị viên.

🌟 1. Tính năng Nổi bật
⭐ Phân hệ Khách hàng (Customer)

Giao diện thân thiện – tối ưu trải nghiệm người dùng

Đặt vé Real-time

Sơ đồ ghế trực quan

Cơ chế giữ ghế (Seat Locking) trong 10 phút
→ Ngăn người dùng trùng ghế

Thanh toán Online – Tích hợp VNPAY

Môi trường Sandbox/Test

Vé điện tử (E-Ticket)

Gửi email kèm QR Code sau khi thanh toán thành công

Thành viên & Tích điểm

Tự động tích điểm

Thăng hạng: Bạc → Vàng → Kim Cương

Đánh giá phim

Chấm điểm & bình luận sau khi xem phim

⭐ Phân hệ Quản trị (Admin / Staff)
📊 Dashboard Tổng quan

Theo dõi KPI theo thời gian thực:

Doanh thu

Vé bán

Suất chiếu

🧠 Advanced Analytics (Phân tích nâng cao)

Biểu đồ xu hướng doanh thu ngày / tháng

Heatmap (Biểu đồ nhiệt) để phân tích khung giờ "vàng"

Hiệu suất phòng chiếu:

Tỷ lệ lấp đầy (Occupancy Rate)

Top phim doanh thu cao nhất

Bộ lọc thời gian tùy chỉnh

🛠 Quản lý Tài nguyên (CRUD)

Phim

Phòng chiếu (IMAX, 4DX, Standard…)

Suất chiếu

Voucher

Người dùng (Phân quyền Staff/Customer)

🛠 2. Cài đặt & Chạy thử

Dự án bao gồm sẵn db.sqlite3 chứa hàng nghìn dữ liệu mẫu
→ Có thể trải nghiệm Dashboard ngay lập tức.

📌 Yêu cầu tiên quyết

Python 3.10+

Git

🚀 Bước 1: Clone dự án:

git clone https://github.com/lequan2109/cinema_project.git

cd cinema_project

🚀 Bước 2: Tạo môi trường ảo (Virtual Environment):

Windows
python -m venv venv

venv\Scripts\activate

macOS / Linux

python3 -m venv venv

source venv/bin/activate

🚀 Bước 3: Cài đặt thư viện:

pip install -r requirements.txt

🚀 Bước 4: Khởi chạy server:


Dự án có sẵn database → không cần chạy migrations

python manage.py runserver


Truy cập:

👉 http://127.0.0.1:8000/

🔐 3. Tài khoản Demo (Test)

Vai trò	          Tài khoản	    Mật khẩu	          Chức năng
Quản trị (Staff)	staff	        123	                 Dashboard, Analytics, CRUD
Khách hàng	      customer	    123	                 Đặt vé, lịch sử vé, đánh giá phim
Khách hàng 2	    user_001	    123	                 Test tính năng giữ ghế
📄 4. Góp ý – Đóng góp

Rất hoan nghênh mọi ý tưởng và đóng góp để dự án hoàn thiện hơn.
Nếu bạn muốn mở PR/issue, cứ thoải mái nhé!



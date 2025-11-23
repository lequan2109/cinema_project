🎬 Cinema Pro - Hệ thống Đặt vé & Phân tích Dữ liệu Rạp chiếu phim
Cinema Pro là một nền tảng quản lý rạp chiếu phim toàn diện được xây dựng bằng Django Framework. Hệ thống tích hợp quy trình đặt vé thời gian thực, thanh toán điện tử VNPAY và đặc biệt là Dashboard phân tích dữ liệu (Data Analytics) chuyên sâu dành cho quản trị viên.

🌟 Tính năng Nổi bật
1. Phân hệ Khách hàng (Customer)
Giao diện thân thiện. 

Đặt vé Real-time:

Sơ đồ ghế trực quan.

Cơ chế giữ ghế (Locking): Ngăn chặn 2 người cùng chọn 1 ghế trong 10 phút để tránh trùng lặp.

Thanh toán Online: Tích hợp cổng thanh toán VNPAY (Môi trường Sandbox/Test).

Vé điện tử (E-Ticket): Nhận vé kèm mã QR qua Email ngay sau khi thanh toán thành công.

Thành viên & Tích điểm: Tự động tích điểm khi mua vé và thăng hạng thành viên (Bạc, Vàng, Kim Cương).

Đánh giá phim: Hệ thống cho phép người dùng chấm điểm và viết bình luận sau khi đã xem phim.

2. Phân hệ Quản trị (Admin/Staff)
Dashboard Tổng quan: Theo dõi các chỉ số KPI: Doanh thu, Vé bán, Suất chiếu theo thời gian thực.

📊 Advanced Analytics (Phân tích nâng cao):

Biểu đồ xu hướng: Theo dõi doanh thu theo ngày/tháng.

Heatmap (Biểu đồ nhiệt): Phân tích khung giờ "vàng" đông khách nhất trong tuần để tối ưu lịch chiếu.

Phân tích hiệu suất: Top phim doanh thu cao, tỷ lệ lấp đầy phòng chiếu (Occupancy Rate).

Bộ lọc: Lọc báo cáo theo khoảng thời gian tùy chỉnh.

Quản lý Tài nguyên (CRUD):

Quản lý Phim, Phòng chiếu (IMAX, 4DX, Standard...), Suất chiếu.

Quản lý Mã giảm giá (Voucher).

Quản lý Người dùng (Phân quyền Staff/Customer).

🛠 Cài đặt và Chạy thử
Dự án này đã bao gồm sẵn cơ sở dữ liệu mẫu (db.sqlite3) chứa hàng nghìn dữ liệu vé và phim để bạn có thể trải nghiệm các biểu đồ phân tích ngay lập tức mà không cần nhập liệu thủ công.

Yêu cầu tiên quyết
Python 3.10 trở lên.

Git.

Bước 1: Clone dự án về máy
Mở Terminal (hoặc CMD/PowerShell) và chạy lệnh:

bash
git clone https://github.com/lequan2109/cinema_project.git
cd cinema_project



Bước 2: Tạo môi trường ảo (Virtual Environment)
Khuyến khích dùng môi trường ảo để không ảnh hưởng đến Python gốc của máy.

Đối với Windows:

bash
python -m venv venv
venv\Scripts\activate
Đối với macOS/Linux:

bash
python3 -m venv venv
source venv/bin/activate



Bước 3: Cài đặt các thư viện phụ thuộc
bash
pip install -r requirements.txt


Bước 4: Khởi chạy Server
Dự án đã có sẵn file db.sqlite3, bạn không cần chạy migrations. Chỉ cần chạy server:

bash
python manage.py runserver
Truy cập vào địa chỉ: http://127.0.0.1:8000/

🔐 Tài khoản Demo (Có sẵn)
Hệ thống đã có sẵn dữ liệu người dùng để bạn test các quyền hạn khác nhau:

Vai trò	           Tài khoản	 Mật khẩu	       Chức năng trải nghiệm
Quản trị (Staff)	staff	       123	           Xem Dashboard, Analytics, Quản lý phim/lịch chiếu/user
Khách hàng	      customer	   123	           Đặt vé, Xem lịch sử vé, Đánh giá phim, Tích điểm
Khách hàng 2	    user_001	   123	           Test tính năng giữ ghế (Locking)

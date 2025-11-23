# Đường dẫn: cinema_app/utils.py

import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings

def send_eticket_email(user, booking_code, tickets, total_price):
    """
    Hàm tạo QR code và gửi email vé điện tử cho khách hàng
    """
    try:
        # 1. Tạo nội dung QR Code (Chứa mã booking)
        qr_data = f"BOOKING:{booking_code}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Lưu ảnh vào bộ nhớ đệm (Buffer)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # 2. Tạo nội dung Email
        subject = f"Vé điện tử - Đơn hàng #{booking_code}"
        movie_title = tickets[0].showtime.movie.title
        showtime_str = tickets[0].showtime.start_time.strftime("%H:%M %d/%m/%Y")
        room_name = tickets[0].showtime.room.name
        seats = ", ".join([t.seat_label() for t in tickets])
        
        body = f"""
        Xin chào {user.username},
        
        Cảm ơn bạn đã đặt vé tại Cinema. Dưới đây là thông tin vé của bạn:
        
        ----------------------------------------
        Phim: {movie_title}
        Suất chiếu: {showtime_str}
        Rạp: {room_name}
        Ghế: {seats}
        ----------------------------------------
        Tổng tiền: {total_price:,.0f} đ
        Mã đơn hàng: {booking_code}
        
        Vui lòng đưa mã QR đính kèm cho nhân viên soát vé khi đến rạp.
        
        Chúc bạn xem phim vui vẻ!
        """

        # 3. Gửi Email
        email = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@cinema.com',
            [user.email],
        )
        
        # Đính kèm ảnh QR
        email.attach(f'qrcode_{booking_code}.png', buffer.getvalue(), 'image/png')
        email.send()
        
        print(f"✅ Đã gửi vé điện tử đến {user.email}")
        
    except Exception as e:
        print(f"❌ Lỗi gửi email: {str(e)}")
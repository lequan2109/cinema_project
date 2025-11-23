# Đường dẫn: cinema_app/seed.py

import random
import datetime
import pytz
import uuid
from django.db import transaction
from django.utils import timezone # Đã thêm import này để sửa lỗi NameError
from django.contrib.auth.models import User
from cinema_app.models import ShowTime, Ticket, Review, Movie

# --- CẤU HÌNH ---
TZ = pytz.timezone('Asia/Ho_Chi_Minh')

# Review mẫu
COMMENTS_GOOD = [
    "Phim đỉnh của chóp! Kỹ xảo 10/10.", "Xem xong vẫn còn nổi da gà.", "Cốt truyện cuốn hút từ đầu đến cuối.", 
    "Không uổng công chờ đợi cả năm trời.", "Rạp âm thanh quá đã, xem hành động phê lòi.", "Diễn viên đóng đạt, xúc động.",
    "Siêu phẩm của năm, chắc chắn sẽ đi xem lại.", "Mãn nhãn phần nhìn, đã tai phần nghe.", "Cười bể bụng, giải trí cực tốt.",
    "Đoạn kết bất ngờ không đỡ được!"
]
COMMENTS_BAD = [
    "Hơi thất vọng, kịch bản lỏng lẻo.", "Phim dài dòng, ngồi tê cả chân.", "Kỹ xảo hơi giả trân đoạn cuối.", 
    "Diễn xuất hơi đơ, chưa tới cảm xúc.", "Nội dung dễ đoán, không có gì mới mẻ.", "Âm thanh hơi chói tai.",
    "Không hay như lời đồn.", "Cái kết hơi hụt hẫng."
]

@transaction.atomic
def run():
    print("🚀 BẮT ĐẦU DÀN TRẢI LẠI DỮ LIỆU VÉ (RE-BOOKING)...")
    
    # === 1. XÓA VÉ VÀ REVIEW CŨ (ĐỂ LÀM SẠCH BIỂU ĐỒ) ===
    print("   🗑️  Đang xóa toàn bộ vé và đánh giá cũ (Giữ nguyên Phim/Lịch chiếu)...")
    Ticket.objects.all().delete()
    Review.objects.all().delete()

    # === 2. LẤY DỮ LIỆU CẦN THIẾT ===
    all_users = list(User.objects.filter(profile__role='CUSTOMER'))
    all_showtimes = ShowTime.objects.all().select_related('room', 'movie')
    count_showtimes = all_showtimes.count()
    
    print(f"   📅 Tìm thấy {count_showtimes} suất chiếu. Đang tiến hành đặt vé lại...")

    if count_showtimes == 0:
        print("   ⚠️ Không tìm thấy suất chiếu nào! Vui lòng chạy script tạo lịch chiếu trước.")
        return

    total_tickets = 0
    now = timezone.now()

    # === 3. DUYỆT QUA TỪNG SUẤT CHIẾU ĐỂ ĐẶT VÉ ===
    for i, st in enumerate(all_showtimes):
        # Chỉ in tiến độ mỗi 100 suất để đỡ lag terminal
        if i % 100 == 0: print(f"   ... Đang xử lý suất chiếu thứ {i}/{count_showtimes} ...")

        # Logic: 
        # - Nếu suất chiếu đã qua (Quá khứ): Bán nhiều vé (60% - 95% rạp)
        # - Nếu suất chiếu chưa tới (Tương lai): Bán ít hoặc không bán (0% - 30% rạp)
        
        is_past = st.start_time < now
        
        if is_past:
            occupancy = random.uniform(0.6, 0.95) # Lấp đầy cao để biểu đồ đẹp
        else:
            occupancy = random.uniform(0.0, 0.3)  # Tương lai vắng hơn

        seats_to_sell = int(st.room.total_seats * occupancy)
        if seats_to_sell == 0: continue

        # Sinh danh sách ghế
        all_seats = [(chr(65+r), c) for r in range(st.room.rows) for c in range(1, st.room.cols + 1)]
        sold_seats = random.sample(all_seats, min(seats_to_sell, len(all_seats)))

        # Bắt đầu đặt vé theo nhóm
        idx = 0
        while idx < len(sold_seats):
            if not all_users: break 
            user = random.choice(all_users)
            
            # Một booking mua 1-6 vé
            num_tickets = random.randint(1, 6)
            tickets_in_batch = sold_seats[idx : idx + num_tickets]
            idx += num_tickets
            
            booking_code = f"{user.id}-{int(st.start_time.timestamp())}-{uuid.uuid4().hex[:4]}"
            
            # Tính thời gian đặt vé (Booked At)
            # Vé thường được mua trước giờ chiếu từ 1 tiếng đến 3 ngày
            # QUAN TRỌNG: Phải dựa vào st.start_time để dàn trải ngày
            delta_days = random.randint(0, 3)
            delta_hours = random.randint(1, 24)
            fake_booked_at = st.start_time - datetime.timedelta(days=delta_days, hours=delta_hours)
            
            # Đảm bảo không bị lỗi thời gian âm quá xa (nếu có)
            if fake_booked_at > now: fake_booked_at = now

            for r_seat, c_seat in tickets_in_batch:
                # Tạo vé (Lúc này booked_at sẽ bị auto_now_add set là NOW)
                ticket = Ticket.objects.create(
                    user=user, 
                    showtime=st, 
                    seat_row=r_seat, 
                    seat_number=c_seat,
                    price_paid=st.base_price, 
                    is_paid=True, # Đã thanh toán hết để hiện lên báo cáo
                    booking_code=booking_code
                )
                
                # *** KỸ THUẬT QUAN TRỌNG ***
                # Update trực tiếp vào DB để ghi đè thời gian 'booked_at'
                # Giúp biểu đồ dàn trải theo đúng ngày thực tế của suất chiếu
                Ticket.objects.filter(pk=ticket.pk).update(booked_at=fake_booked_at)
                
                total_tickets += 1

            # Tạo Review (Nếu là suất quá khứ)
            if is_past and random.random() < 0.15: # 15% xác suất viết review
                if not Review.objects.filter(user=user, movie=st.movie).exists():
                    rating = random.choices([5, 4, 3, 2, 1], weights=[45, 35, 10, 5, 5])[0]
                    comment_pool = COMMENTS_GOOD if rating >= 4 else COMMENTS_BAD
                    
                    Review.objects.create(
                        user=user, 
                        movie=st.movie, 
                        rating=rating, 
                        comment=random.choice(comment_pool)
                    )

    print(f"✅ HOÀN TẤT! Đã dàn trải lại {total_tickets} vé trên {count_showtimes} suất chiếu.")
    print(f"   👉 Vào 'Quản lý -> Phân tích (DA)' để xem biểu đồ chạy mượt từ tháng 10 đến nay!")

if __name__ == "__main__":
    run()
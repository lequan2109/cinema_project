# Đường dẫn: cinema_app/seed.py

# Import tất cả các thư viện và model cần thiết
import datetime
import pytz
from django.db import transaction
from django.contrib.auth.models import User
from cinema_app.models import Profile, Movie, CinemaRoom, Promotion, ShowTime, Ticket

# Bọc tất cả trong một transaction
# Nếu có lỗi, toàn bộ sẽ được khôi phục, tránh làm hỏng DB
@transaction.atomic
def run():
    
    # === 1. XÓA DỮ LIỆU CŨ ===
    # Xóa vé, suất chiếu, khuyến mãi, phim, phòng. 
    # KHÔNG xóa User và Profile để giữ tài khoản của bạn.
    print("Deleting old data...")
    Ticket.objects.all().delete()
    ShowTime.objects.all().delete()
    Promotion.objects.all().delete()
    Movie.objects.all().delete()
    CinemaRoom.objects.all().delete()

    # === 2. TẠO USERS VÀ PROFILES ===
    # Lấy timezone chuẩn của Việt Nam
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    # Lấy hoặc tạo user STAFF
    staff_user, created = User.objects.get_or_create(username='staff')
    if created:
        staff_user.set_password('123')
        staff_user.is_staff = True
        staff_user.save()
        Profile.objects.create(user=staff_user, full_name='Nhân Viên Mẫu', role='STAFF')
        print(f"Created user 'staff' (pass: 123)")
    else:
        Profile.objects.get_or_create(user=staff_user, defaults={'role': 'STAFF'})

    # Lấy hoặc tạo user CUSTOMER
    customer_user, created = User.objects.get_or_create(username='customer')
    if created:
        customer_user.set_password('123')
        customer_user.save()
        Profile.objects.create(user=customer_user, full_name='Khách Hàng Mẫu 1', role='CUSTOMER')
        print(f"Created user 'customer' (pass: 123)")
    else:
        Profile.objects.get_or_create(user=customer_user, defaults={'role': 'CUSTOMER'})

    # Lấy hoặc tạo user CUSTOMER 2
    customer2_user, created = User.objects.get_or_create(username='customer2')
    if created:
        customer2_user.set_password('123')
        customer2_user.save()
        Profile.objects.create(user=customer2_user, full_name='Khách Hàng Mẫu 2', role='CUSTOMER')
        print(f"Created user 'customer2' (pass: 123)")
    else:
        Profile.objects.get_or_create(user=customer2_user, defaults={'role': 'CUSTOMER'})

    print("--- Users & Profiles created.")

    # === 3. TẠO PHÒNG CHIẾU ===
    room1 = CinemaRoom.objects.create(name="Phòng 1", rows=8, cols=12) # 96 ghế
    room2 = CinemaRoom.objects.create(name="Phòng 2 (IMAX)", rows=10, cols=15) # 150 ghế
    room3 = CinemaRoom.objects.create(name="Phòng 3 (VIP)", rows=6, cols=8) # 48 ghế
    print(f"--- 3 Cinema Rooms created (Room 1: {room1.rows}x{room1.cols}, Room 2: {room2.rows}x{room2.cols}, Room 3: {room3.rows}x{room3.cols}).")

    # === 4. TẠO PHIM ===
    # (Giả định hôm nay là 30/10/2025)
    today = datetime.date(2025, 10, 30)
    
    # --- Phim Đang Chiếu (release_date trong quá khứ) ---
    movie_dune = Movie.objects.create(
        title="Dune: Hành Tinh Cát - Phần Hai",
        description="Theo chân Paul Atreides khi anh hợp nhất với Chani và người Fremen, đồng thời tìm cách trả thù những kẻ đã hủy hoại gia đình anh.",
        duration=166, genre="Khoa học viễn tưởng", release_date=today - datetime.timedelta(days=200), age_limit=16,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/U2Qp5pL3ovA" frameborder="0" allowfullscreen></iframe>'
    )
    
    movie_mai = Movie.objects.create(
        title="Mai",
        description="Câu chuyện về Mai, một nhân viên massage gần 40 tuổi, tình cờ gặp Dương, một nhạc công đào hoa. Cả hai bị cuốn vào một mối tình lãng mạn bất chấp sự chênh lệch tuổi tác và định kiến xã hội.",
        duration=131, genre="Tình cảm, Tâm lý", release_date=today - datetime.timedelta(days=250), age_limit=18,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/vH-q-Qdsm-I" frameborder="0" allowfullscreen></iframe>'
    )

    movie_panda = Movie.objects.create(
        title="Kung Fu Panda 4",
        description="Sau ba cuộc phiêu lưu, gấu trúc Po được kêu gọi trở thành Lãnh đạo Tinh thần của Thung lũng Hòa bình. Tuy nhiên, cậu cần tìm và huấn luyện một Chiến binh Rồng mới trước khi có thể đảm nhận vị trí.",
        duration=94, genre="Hoạt hình, Hài", release_date=today - datetime.timedelta(days=150), age_limit=0,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/Svr-xXVL-2w" frameborder="0" allowfullscreen></iframe>'
    )
    
    movie_exhuma = Movie.objects.create(
        title="Exhuma: Quật Mộ Trùng Ma",
        description="Một pháp sư, một thầy phong thủy và một chuyên gia tang lễ hợp tác để điều tra một loạt sự kiện siêu nhiên bí ẩn ảnh hưởng đến một gia đình giàu có, dẫn họ đến một ngôi mộ bị nguyền rủa.",
        duration=134, genre="Kinh dị, Siêu nhiên", release_date=today - datetime.timedelta(days=100), age_limit=18,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/kGfYR695nhE" frameborder="0" allowfullscreen></iframe>'
    )

    movie_oppen = Movie.objects.create(
        title="Oppenheimer",
        description="Câu chuyện về nhà vật lý lý thuyết J. Robert Oppenheimer, người đứng đầu phòng thí nghiệm Los Alamos trong dự án Manhattan, nơi đã phát triển quả bom nguyên tử đầu tiên.",
        duration=180, genre="Tiểu sử, Lịch sử", release_date=today - datetime.timedelta(days=300), age_limit=18,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/bK6ldnjE3Y0" frameborder="0" allowfullscreen></iframe>'
    )

    # --- Phim Sắp Chiếu (release_date trong tương lai) ---
    movie_joker = Movie.objects.create(
        title="Joker: Folie à Deux",
        description="Phần tiếp theo của 'Joker' (2019), khám phá mối quan hệ phức tạp giữa Arthur Fleck và Bác sĩ Harleen Quinzel tại Bệnh viện Arkham.",
        duration=140, genre="Tội phạm, Nhạc kịch", release_date=today + datetime.timedelta(days=15), age_limit=18,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/tZ57SBF7-uY" frameborder="0" allowfullscreen></iframe>'
    )

    movie_moana = Movie.objects.create(
        title="Moana 2",
        description="Moana nhận được một cuộc gọi bất ngờ từ tổ tiên, đưa cô vào một cuộc hành trình mới đến vùng biển xa xôi của Châu Đại Dương.",
        duration=100, genre="Hoạt hình, Phiêu lưu", release_date=today + datetime.timedelta(days=28), age_limit=0,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/CpOAt-s2iSg" frameborder="0" allowfullscreen></iframe>'
    )

    movie_deadpool = Movie.objects.create(
        title="Deadpool & Wolverine",
        description="Wolverine đang hồi phục sau vết thương thì chạm trán với Deadpool. Họ hợp tác để đánh bại một kẻ thù chung.",
        duration=127, genre="Hành động, Hài", release_date=today + datetime.timedelta(days=45), age_limit=18,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/11RIqA-Sr64" frameborder="0" allowfullscreen></iframe>'
    )

    movie_wicked = Movie.objects.create(
        title="Wicked: Phần Một",
        description="Câu chuyện về Elphaba, một cô gái trẻ bị hiểu lầm vì làn da xanh của mình, và mối quan hệ của cô với Galinda, người sau này trở thành Phù thủy tốt bụng Glinda.",
        duration=150, genre="Nhạc kịch, Fantasy", release_date=today + datetime.timedelta(days=60), age_limit=0,
        trailer_url='<iframe width="560" height="315" src="https://www.youtube.com/embed/F1dvX92nOqg" frameborder="0" allowfullscreen></iframe>'
    )
    print(f"--- 9 Movies created (5 now showing, 4 coming soon).")

    # === 5. TẠO KHUYẾN MÃI ===
    Promotion.objects.create(code="XINCHAO", discount_percent=15, valid_until=today + datetime.timedelta(days=60), is_active=True)
    Promotion.objects.create(code="TANG50K", discount_percent=50, valid_until=today + datetime.timedelta(days=30), is_active=True)
    Promotion.objects.create(code="BLACKFRIDAY", discount_percent=30, valid_until=datetime.date(2025, 11, 29), is_active=True)
    Promotion.objects.create(code="HETHAN", discount_percent=50, valid_until=today - datetime.timedelta(days=1), is_active=True)
    Promotion.objects.create(code="TAMKHOA", discount_percent=20, valid_until=today + datetime.timedelta(days=60), is_active=False)
    print("--- 5 Promotions created.")

    # === 6. TẠO SUẤT CHIẾU ===
    # Suất chiếu QUÁ KHỨ (cho báo cáo)
    show_past1 = ShowTime.objects.create(movie=movie_mai, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 28, 19, 0)), base_price=100000)
    show_past2 = ShowTime.objects.create(movie=movie_oppen, room=room2, start_time=tz.localize(datetime.datetime(2025, 10, 28, 20, 0)), base_price=150000)
    show_past3 = ShowTime.objects.create(movie=movie_dune, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 29, 19, 0)), base_price=120000)
    show_past4 = ShowTime.objects.create(movie=movie_exhuma, room=room3, start_time=tz.localize(datetime.datetime(2025, 10, 29, 21, 0)), base_price=130000)
    show_past5 = ShowTime.objects.create(movie=movie_panda, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 29, 17, 0)), base_price=80000)

    # Suất chiếu TƯƠNG LAI (để đặt vé)
    # Hôm nay (30/10/2025)
    show_future1 = ShowTime.objects.create(movie=movie_dune, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 30, 19, 0)), base_price=120000)
    show_future2 = ShowTime.objects.create(movie=movie_dune, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 30, 21, 30)), base_price=120000)
    show_future3 = ShowTime.objects.create(movie=movie_exhuma, room=room3, start_time=tz.localize(datetime.datetime(2025, 10, 30, 20, 0)), base_price=180000) # Phòng VIP
    show_future4 = ShowTime.objects.create(movie=movie_mai, room=room2, start_time=tz.localize(datetime.datetime(2025, 10, 30, 20, 15)), base_price=110000)
    
    # Ngày mai (31/10/2025)
    ShowTime.objects.create(movie=movie_panda, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 31, 17, 0)), base_price=80000)
    ShowTime.objects.create(movie=movie_panda, room=room1, start_time=tz.localize(datetime.datetime(2025, 10, 31, 19, 0)), base_price=90000)
    ShowTime.objects.create(movie=movie_dune, room=room2, start_time=tz.localize(datetime.datetime(2025, 10, 31, 20, 0)), base_price=130000)
    ShowTime.objects.create(movie=movie_exhuma, room=room3, start_time=tz.localize(datetime.datetime(2025, 10, 31, 22, 0)), base_price=180000)
    ShowTime.objects.create(movie=movie_mai, room=room2, start_time=tz.localize(datetime.datetime(2025, 10, 31, 19, 30)), base_price=110000)
    ShowTime.objects.create(movie=movie_oppen, room=room2, start_time=tz.localize(datetime.datetime(2025, 10, 31, 14, 0)), base_price=140000)

    # Tuần sau
    ShowTime.objects.create(movie=movie_dune, room=room1, start_time=tz.localize(datetime.datetime(2025, 11, 5, 19, 0)), base_price=120000)
    ShowTime.objects.create(movie=movie_dune, room=room1, start_time=tz.localize(datetime.datetime(2025, 11, 5, 21, 30)), base_price=120000)
    ShowTime.objects.create(movie=movie_mai, room=room2, start_time=tz.localize(datetime.datetime(2025, 11, 5, 20, 15)), base_price=110000)
    ShowTime.objects.create(movie=movie_panda, room=room1, start_time=tz.localize(datetime.datetime(2025, 11, 6, 17, 0)), base_price=80000)
    ShowTime.objects.create(movie=movie_panda, room=room1, start_time=tz.localize(datetime.datetime(2025, 11, 6, 19, 0)), base_price=90000)
    ShowTime.objects.create(movie=movie_dune, room=room2, start_time=tz.localize(datetime.datetime(2025, 11, 7, 20, 0)), base_price=130000)
    ShowTime.objects.create(movie=movie_exhuma, room=room3, start_time=tz.localize(datetime.datetime(2025, 11, 7, 22, 0)), base_price=180000)
    
    print(f"--- 17 ShowTimes created (5 past, 12 future).")

    # === 7. TẠO VÉ ===
    
    # --- Vé QUÁ KHỨ (cho báo cáo) ---
    Ticket.objects.create(user=customer_user, showtime=show_past1, seat_row="A", seat_number=1, price_paid=100000, is_paid=True, booked_at=show_past1.start_time - datetime.timedelta(days=1))
    Ticket.objects.create(user=customer_user, showtime=show_past1, seat_row="A", seat_number=2, price_paid=100000, is_paid=True, booked_at=show_past1.start_time - datetime.timedelta(days=1))
    
    Ticket.objects.create(user=customer2_user, showtime=show_past2, seat_row="C", seat_number=5, price_paid=150000, is_paid=True, booked_at=show_past2.start_time - datetime.timedelta(days=1))
    Ticket.objects.create(user=customer2_user, showtime=show_past2, seat_row="C", seat_number=6, price_paid=150000, is_paid=True, booked_at=show_past2.start_time - datetime.timedelta(days=1))
    Ticket.objects.create(user=customer_user, showtime=show_past2, seat_row="D", seat_number=10, price_paid=150000, is_paid=True, booked_at=show_past2.start_time - datetime.timedelta(hours=5))
    
    Ticket.objects.create(user=customer_user, showtime=show_past3, seat_row="E", seat_number=8, price_paid=120000, is_paid=True, booked_at=show_past3.start_time - datetime.timedelta(days=2))
    
    Ticket.objects.create(user=customer2_user, showtime=show_past4, seat_row="F", seat_number=3, price_paid=130000, is_paid=True, booked_at=show_past4.start_time - datetime.timedelta(hours=10))
    Ticket.objects.create(user=customer2_user, showtime=show_past4, seat_row="F", seat_number=4, price_paid=130000, is_paid=True, booked_at=show_past4.start_time - datetime.timedelta(hours=10))
    
    Ticket.objects.create(user=customer_user, showtime=show_past5, seat_row="B", seat_number=7, price_paid=80000, is_paid=True, booked_at=show_past5.start_time - datetime.timedelta(days=1))
    Ticket.objects.create(user=customer_user, showtime=show_past5, seat_row="B", seat_number=8, price_paid=80000, is_paid=True, booked_at=show_past5.start_time - datetime.timedelta(days=1))

    # --- Vé TƯƠNG LAI (để chặn ghế) ---
    # Chặn 3 ghế cho suất chiếu DUNE tối nay
    Ticket.objects.create(user=staff_user, showtime=show_future1, seat_row="C", seat_number=5, price_paid=0, is_paid=True, booked_at=tz.localize(datetime.datetime.now()))
    Ticket.objects.create(user=staff_user, showtime=show_future1, seat_row="C", seat_number=6, price_paid=0, is_paid=True, booked_at=tz.localize(datetime.datetime.now()))
    Ticket.objects.create(user=staff_user, showtime=show_future1, seat_row="C", seat_number=7, price_paid=0, is_paid=True, booked_at=tz.localize(datetime.datetime.now()))

    # Chặn 2 ghế cho suất chiếu EXHUMA tối nay
    Ticket.objects.create(user=staff_user, showtime=show_future3, seat_row="A", seat_number=3, price_paid=0, is_paid=True, booked_at=tz.localize(datetime.datetime.now()))
    Ticket.objects.create(user=staff_user, showtime=show_future3, seat_row="A", seat_number=4, price_paid=0, is_paid=True, booked_at=tz.localize(datetime.datetime.now()))
    
    print(f"--- 15 Tickets created (10 past for reports, 5 future for blocking).")
    print("\n✅✅✅ SAMPLE DATA CREATED SUCCESSFULLY! ✅✅✅")
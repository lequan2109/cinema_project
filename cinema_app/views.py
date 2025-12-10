# ==============================================================================
# PHẦN 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT
# ==============================================================================

# 1. Các module cốt lõi của Django để xử lý Request/Response và Giao diện
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse  # Trả về dữ liệu JSON cho API (AJAX)
from django.contrib import messages   # Hiển thị thông báo (Thành công/Lỗi) cho người dùng

# 2. Module xác thực và quản lý người dùng (Auth System)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test # Decorators bảo vệ view
from django.contrib.auth.models import User # Model người dùng mặc định

# 3. Các module xử lý Database và Truy vấn nâng cao (ORM)
from django.db import transaction, IntegrityError # Quản lý giao dịch (Transaction) an toàn
from django.db.models import Sum, Count, F, Q # Các hàm tổng hợp và điều kiện lọc phức tạp (AND/OR)
from django.db.models.functions import TruncDate, ExtractWeekDay, ExtractHour # Xử lý ngày tháng trong SQL

# 4. Các module xử lý Thời gian và Tiện ích
from django.utils import timezone
from datetime import date, datetime, timedelta
from collections import defaultdict
import json # Xử lý dữ liệu JSON gửi lên từ Frontend
import uuid # Tạo mã định danh duy nhất (nếu cần)

# 5. Module Cache và Validator
from django.views.decorators.http import require_POST # Chỉ cho phép method POST
from django.core.cache import cache # Hệ thống Cache (lưu trữ RAM) để giữ ghế Realtime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# 6. Các file nội bộ của dự án
from . import vnpay_helpers, utils # Thư viện thanh toán VNPAY và gửi Email
from .models import Movie, CinemaRoom, ShowTime, Ticket, Promotion, Profile, Review, Food, FoodOrder, FoodOrderItem # Các bảng dữ liệu
from .forms import ( # Các biểu mẫu nhập liệu
    RegisterForm, LoginForm, MovieForm, RoomForm, ShowTimeForm, 
    PromotionForm, BookingForm, ReviewForm, ManageUserForm, FoodOrderForm, FoodManageForm
)

# ==============================================================================
# PHẦN 2: CÁC HÀM PHỤ TRỢ (HELPERS)
# ==============================================================================

def is_staff_user(user):
    """
    Hàm kiểm tra quyền truy cập:
    - Input: Đối tượng User.
    - Logic: Kiểm tra xem user có role là 'STAFF' hoặc cờ is_staff=True không.
    - Mục đích: Dùng cho decorator @user_passes_test để bảo vệ các trang quản trị.
    """
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 'STAFF' or user.is_staff
    except Profile.DoesNotExist:
        return user.is_staff

def get_all_genres():
    """
    Hàm lấy danh sách thể loại phim:
    - Logic: Quét cột 'genre' của toàn bộ phim, tách chuỗi (ví dụ 'Hành động, Hài' -> ['Hành động', 'Hài']).
    - Mục đích: Đổ dữ liệu vào dropdown 'Lọc theo thể loại' ở trang chủ.
    """
    raw_genres = Movie.objects.values_list('genre', flat=True).distinct()
    unique_genres = set()
    
    for g_str in raw_genres:
        if g_str:
            parts = [x.strip() for x in g_str.split(',')]
            for p in parts:
                if p: unique_genres.add(p)
                
    return sorted(list(unique_genres))

# ==============================================================================
# PHẦN 3: PUBLIC VIEWS (TRANG DÀNH CHO KHÁCH HÀNG)
# ==============================================================================

def home(request):
    """
    TRANG CHỦ WEBSITE
    - Chức năng: 
      1. Hiển thị phim 'Đang chiếu' và 'Sắp chiếu'.
      2. Xử lý tìm kiếm và lọc phim.
      3. Hiển thị lịch chiếu sắp tới.
    - Công nghệ: Django ORM filter, Q objects (tìm kiếm), Slice (cắt danh sách).
    """
    today = timezone.localdate()
    
    # 1. Lấy tham số từ URL (?q=...&genre=...)
    q = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()

    # 2. Query cơ bản phân loại phim theo ngày phát hành
    now_showing_movies = Movie.objects.filter(
        release_date__lte=today,
        showtime__start_time__gte=timezone.now()
    ).distinct().order_by('-release_date')
    
    coming_soon_movies = Movie.objects.filter(
        release_date__gt=today
    ).order_by('release_date')

    # 3. Áp dụng bộ lọc (Nếu người dùng có tìm kiếm)
    if q:
        now_showing_movies = now_showing_movies.filter(title__icontains=q)
        coming_soon_movies = coming_soon_movies.filter(title__icontains=q)
    
    if selected_genre:
        now_showing_movies = now_showing_movies.filter(genre__icontains=selected_genre)
        coming_soon_movies = coming_soon_movies.filter(genre__icontains=selected_genre)

    # 4. Lấy danh sách suất chiếu sắp tới (cho Tab Lịch chiếu)
    upcoming_showtimes_qs = ShowTime.objects.filter(
        start_time__gte=timezone.now()
    ).select_related('movie', 'room').order_by('start_time')

    if selected_genre:
        upcoming_showtimes_qs = upcoming_showtimes_qs.filter(movie__genre__icontains=selected_genre)

    # Chỉ lấy 12 suất chiếu đầu tiên để hiển thị cho gọn
    upcoming_showtimes = upcoming_showtimes_qs[:12]

    return render(request, 'cinema_app/home.html', {
        'now_showing_movies': now_showing_movies,
        'coming_soon_movies': coming_soon_movies,
        'upcoming_showtimes': upcoming_showtimes,
        'genres': get_all_genres(),
        'selected_genre': selected_genre,
        'q': q,
    })

def movie_list(request):
    """
    TRANG DANH SÁCH PHIM (KHO PHIM)
    - Chức năng: Hiển thị tất cả phim dạng lưới, hỗ trợ tìm kiếm đầy đủ.
    - Logic: Tương tự trang chủ nhưng không giới hạn số lượng hiển thị.
    """
    today = timezone.localdate()
    q = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()
    
    now_showing_movies = Movie.objects.filter(
        release_date__lte=today
    ).distinct().order_by('-release_date')
    
    coming_soon_movies = Movie.objects.filter(
        release_date__gt=today
    ).order_by('release_date')

    if q:
        now_showing_movies = now_showing_movies.filter(title__icontains=q)
        coming_soon_movies = coming_soon_movies.filter(title__icontains=q)
        
    if selected_genre:
        now_showing_movies = now_showing_movies.filter(genre__icontains=selected_genre)
        coming_soon_movies = coming_soon_movies.filter(genre__icontains=selected_genre)

    return render(request, 'cinema_app/movie_list.html', {
        'now_showing_movies': now_showing_movies,
        'coming_soon_movies': coming_soon_movies,
        'q': q,
        'genres': get_all_genres(),
        'selected_genre': selected_genre,
    })

def movie_detail(request, movie_id):
    """
    TRANG CHI TIẾT PHIM
    - Chức năng: 
      1. Hiển thị thông tin phim, trailer.
      2. Liệt kê các suất chiếu của phim đó.
      3. Cho phép đánh giá (Review) nếu user đã mua vé.
    - Công nghệ: select_related (tối ưu query), Form xử lý.
    """
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes = ShowTime.objects.filter(
        movie=movie, 
        start_time__gte=timezone.now()
    ).select_related('room').order_by('start_time')

    reviews = movie.reviews.all()
    user_can_review = False
    review_form = None

    # Logic kiểm tra quyền đánh giá
    if request.user.is_authenticated:
        has_paid_ticket = Ticket.objects.filter(
            user=request.user, 
            showtime__movie=movie, 
            is_paid=True
        ).exists()
        
        has_reviewed = Review.objects.filter(user=request.user, movie=movie).exists()
        
        if has_paid_ticket and not has_reviewed:
            user_can_review = True
            # Xử lý form gửi đánh giá
            if request.method == 'POST':
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.movie = movie
                    review.user = request.user
                    review.save()
                    messages.success(request, 'Cảm ơn bạn đã đánh giá phim!')
                    return redirect('movie_detail', movie_id=movie.id)
            else:
                review_form = ReviewForm()
    
    return render(request, 'cinema_app/movie_detail.html', {
        'movie': movie,
        'showtimes': showtimes,
        'reviews': reviews,
        'user_can_review': user_can_review,
        'review_form': review_form
    })

def schedule_view(request):
    """
    TRANG LỊCH CHIẾU
    - Chức năng: Xem lịch chiếu theo ngày cụ thể.
    - Logic: Lọc suất chiếu trong khoảng (00:00 -> 23:59) của ngày được chọn.
    """
    movie_id = request.GET.get('movie')
    selected_date_str = request.GET.get('date')

    # Xử lý ngày tháng input
    if not selected_date_str:
        selected_date = timezone.localdate()
        selected_date_str = selected_date.isoformat()
    else:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.localdate()
            selected_date_str = selected_date.isoformat()

    # Tạo khoảng thời gian query (Start of day -> End of day)
    start_of_day_naive = datetime.combine(selected_date, datetime.min.time())
    start_of_day_aware = timezone.make_aware(start_of_day_naive)
    
    if selected_date == timezone.localdate():
        start_of_day_aware = timezone.now() # Nếu là hôm nay thì chỉ lấy giờ tương lai

    end_of_day_aware = start_of_day_aware.replace(hour=23, minute=59, second=59)

    qs = ShowTime.objects.filter(
        start_time__range=(start_of_day_aware, end_of_day_aware)
    ).select_related('movie', 'room').order_by('movie__title', 'start_time')

    if movie_id:
        qs = qs.filter(movie_id=movie_id)

    # Lấy danh sách phim có chiếu trong ngày để hiển thị lọc
    movies_with_showtimes_today = Movie.objects.filter(
        showtime__start_time__range=(start_of_day_aware, end_of_day_aware)
    ).distinct().order_by('title')

    return render(request, 'cinema_app/schedule.html', {
        'showtimes': qs, 
        'movies': movies_with_showtimes_today, 
        'selected_movie': movie_id, 
        'selected_date': selected_date_str 
    })

# ==============================================================================
# PHẦN 4: BOOKING & PAYMENT (ĐẶT VÉ VÀ THANH TOÁN)
# ==============================================================================

@login_required
def booking_view(request, showtime_id):
    """
    TRANG ĐẶT VÉ & CHỌN GHẾ
    - Chức năng: Hiển thị sơ đồ ghế, kiểm tra ghế trống/đã đặt/đang giữ.
    - Logic POST: 
      1. Validate ghế (có ai mua chưa, có ai đang giữ không).
      2. Tạo Ticket với trạng thái is_paid=False.
      3. Gọi VNPAY Helper để tạo URL thanh toán và redirect.
    - Công nghệ: Cache (kiểm tra giữ ghế), Transaction Atomic (chống trùng vé).
    """
    showtime = get_object_or_404(ShowTime, pk=showtime_id)
    room = showtime.room
    
    # Lấy danh sách ghế đã bán (Đã thanh toán thành công)
    taken_seats = set(Ticket.objects.filter(showtime=showtime, is_paid=True).values_list('seat_row', 'seat_number'))
    
    # Lấy danh sách ghế đang bị người khác giữ (Locked in Cache)
    locked_seats = set()
    for r in range(room.rows):
        for c in range(1, room.cols + 1):
            seat_label = f"{chr(ord('A') + r)}{c}"
            cache_key = f"seat_{showtime.id}_{seat_label}"
            locked_by_session = cache.get(cache_key)
            if locked_by_session and locked_by_session != request.session.session_key:
                locked_seats.add((chr(ord('A') + r), c))

    today = date.today()
    promotions = Promotion.objects.all().order_by('-valid_until')

    # Xử lý khi người dùng bấm "Thanh toán"
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['seats']
            promo_code = form.cleaned_data.get('promo_code', '').strip()
            
            # Kiểm tra lại lần cuối xem ghế có hợp lệ không
            seats_taken_or_locked = []
            valid_seats = []
            
            for seat in seats:
                seat = seat.strip()
                if not seat: continue
                try:
                    # Parse ghế (A1 -> Row A, Num 1)
                    seat_row = ''.join([c for c in seat if c.isalpha()]).upper()
                    seat_number = int(''.join([c for c in seat if c.isdigit()]))
                    seat_tuple = (seat_row, seat_number)

                    # Check DB và Cache
                    if seat_tuple in taken_seats:
                        seats_taken_or_locked.append(f"{seat} (đã được mua)")
                        continue
                    
                    cache_key = f"seat_{showtime.id}_{seat}"
                    locked_by = cache.get(cache_key)
                    if locked_by and locked_by != request.session.session_key:
                        seats_taken_or_locked.append(f"{seat} (đang được giữ)")
                        continue

                    valid_seats.append({'label': seat, 'row': seat_row, 'number': seat_number})
                except Exception:
                    pass
            
            if seats_taken_or_locked:
                messages.error(request, f"Rất tiếc! Ghế {', '.join(seats_taken_or_locked)} đã có người khác chọn.")
                return redirect('booking', showtime_id=showtime.id)
            if not valid_seats:
                messages.error(request, "Bạn chưa chọn ghế hợp lệ nào.")
                return redirect('booking', showtime_id=showtime.id)

            # Tính toán tiền và giảm giá
            discount = 0
            if promo_code:
                promo = Promotion.objects.filter(code__iexact=promo_code, is_active=True, valid_until__gte=today).first()
                if promo:
                    discount = promo.discount_percent
                else:
                    messages.warning(request, 'Mã khuyến mãi không hợp lệ.')

            num_seats = len(valid_seats)
            base_price = showtime.base_price
            price_per_seat = (base_price * (100 - discount) / 100)
            total_price = price_per_seat * num_seats
            
            # Tạo Booking Code duy nhất
            booking_time = timezone.now()
            booking_code = f"{request.user.id}-{int(booking_time.timestamp())}-{uuid.uuid4().hex[:4]}"

            try:
                # Mở Transaction để đảm bảo tạo vé an toàn
                with transaction.atomic():
                    for seat_info in valid_seats:
                        Ticket.objects.create(
                            user=request.user,
                            showtime=showtime,
                            booking_code=booking_code,
                            seat_row=seat_info['row'],
                            seat_number=seat_info['number'],
                            price_paid=price_per_seat,
                            is_paid=False, # Chưa thanh toán
                            booked_at=booking_time 
                        )
                        # Xóa cache giữ ghế (đã chuyển sang Ticket DB)
                        cache_key = f"seat_{showtime.id}_{seat_info['label']}"
                        cache.delete(cache_key)
                    
                    # Tạo URL thanh toán VNPAY
                    payment_url = vnpay_helpers.get_vnpay_payment_url(
                        request=request,
                        booking_code=booking_code,
                        total_price=total_price
                    )
                    
                    return redirect(payment_url)

            except IntegrityError:
                messages.error(request, 'Lỗi: Ghế bạn chọn vừa có người khác đặt.')
                return redirect('booking', showtime_id=showtime.id)
    else:
        form = BookingForm()

    # Vẽ sơ đồ ghế (Grid Matrix)
    grid = []
    for r in range(room.rows):
        row_label = chr(ord('A') + r)
        row = []
        for c in range(1, room.cols + 1):
            seat_label = f"{row_label}{c}"
            cache_key = f"seat_{showtime.id}_{seat_label}"
            status = 'available'
            
            if (row_label, c) in taken_seats:
                status = 'taken'
            elif (row_label, c) in locked_seats:
                status = 'locked'
            elif cache.get(cache_key) == request.session.session_key:
                status = 'selected' # Ghế do chính user này đang chọn
            
            row.append({'label': seat_label, 'status': status})
        grid.append({'row_label': row_label, 'seats': row})

    return render(request, 'cinema_app/booking.html', {
        'showtime': showtime,
        'room': room,
        'grid': grid,
        'form': form,
        'promotions': promotions, 
        'today': today,
    })

@login_required
def payment_return_view(request):
    """
    XỬ LÝ KẾT QUẢ THANH TOÁN (IPN / RETURN URL)
    - Chức năng: Nhận phản hồi từ VNPAY sau khi khách thanh toán.
    - Logic:
      1. Kiểm tra Checksum (Chữ ký bảo mật) xem có đúng từ VNPAY gửi không.
      2. Nếu thành công (ResponseCode=00): Cập nhật Ticket -> is_paid=True.
      3. Cộng điểm tích lũy cho User.
      4. Gửi vé điện tử qua Email.
    """
    input_data = request.GET.dict() 
    if not input_data:
        return redirect('my_tickets')

    is_valid, message = vnpay_helpers.verify_vnpay_return(input_data)
    booking_code = input_data.get('vnp_TxnRef')

    if not is_valid:
        # Nếu chữ ký sai hoặc thanh toán lỗi -> Xóa vé tạm
        if booking_code:
            Ticket.objects.filter(booking_code=booking_code, is_paid=False).delete()
        messages.error(request, f"Lỗi thanh toán: {message}")
        return redirect('my_tickets')

    if message == "Thanh toán thành công":
        try:
            tickets_to_pay = Ticket.objects.filter(booking_code=booking_code, is_paid=False)
            
            if not tickets_to_pay.exists():
                return redirect('my_tickets')

            total_amount = tickets_to_pay.aggregate(total=Sum('price_paid'))['total'] or 0
            points_earned = int(total_amount / 1000) # 1000đ = 1 điểm

            with transaction.atomic():
                # 1. Cập nhật vé
                tickets_to_pay.update(is_paid=True)
                # 2. Cộng điểm
                try:
                    profile = request.user.profile
                    profile.points += points_earned
                    profile.update_membership()
                    profile.save()
                    messages.success(request, f"Thanh toán thành công! +{points_earned} điểm.")
                except Profile.DoesNotExist:
                    pass 
            
            # 3. Gửi Email vé
            if request.user.email:
                try:
                    validate_email(request.user.email)
                    tickets_paid = Ticket.objects.filter(booking_code=booking_code)
                    utils.send_eticket_email(request.user, booking_code, tickets_paid, total_amount)
                except Exception:
                    pass # Gửi mail lỗi không ảnh hưởng luồng chính

            return redirect('my_tickets')
                
        except Exception as e:
            messages.error(request, f"Lỗi xử lý đơn hàng: {str(e)}")
            return redirect('my_tickets')
    else:
        # Thanh toán thất bại -> Xóa vé giữ
        if booking_code:
            Ticket.objects.filter(booking_code=booking_code, is_paid=False).delete()
        messages.error(request, f"Giao dịch thất bại: {message}")
        return redirect('my_tickets')

# ==============================================================================
# PHẦN 5: API AJAX (REAL-TIME SEAT LOCKING)
# ==============================================================================

@login_required
@require_POST
def lock_seat(request):
    """
    API GIỮ GHẾ (AJAX)
    - Chức năng: Khóa ghế tạm thời khi người dùng click vào ghế.
    - Công nghệ: Cache (RAM) với thời gian hết hạn (TTL) = 600s (10 phút).
    - Trả về: JSON success hoặc error.
    """
    try:
        if not request.session.session_key: request.session.create()
        data = json.loads(request.body)
        showtime_id = data.get('showtime_id')
        seat_label = data.get('seat_label')
        
        if not showtime_id or not seat_label:
            return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin.'}, status=400)
            
        cache_key = f"seat_{showtime_id}_{seat_label}"
        # cache.add trả về True nếu key chưa tồn tại (Lock thành công), False nếu đã có (Bị khóa)
        is_locked = cache.add(cache_key, request.session.session_key, timeout=600)
        
        if is_locked:
            return JsonResponse({'status': 'success', 'message': 'Giữ ghế thành công.'})
        else:
            # Kiểm tra xem có phải chính mình đang giữ không
            if cache.get(cache_key) == request.session.session_key:
                 return JsonResponse({'status': 'success', 'message': 'Bạn đã giữ ghế này.'})
            return JsonResponse({'status': 'error', 'message': 'Ghế đã bị người khác chọn.'}, status=409)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def release_seat(request):
    """
    API NHẢ GHẾ (AJAX)
    - Chức năng: Xóa ghế khỏi cache khi người dùng bỏ chọn.
    """
    try:
        data = json.loads(request.body)
        showtime_id = data.get('showtime_id')
        seat_label = data.get('seat_label')
        
        cache_key = f"seat_{showtime_id}_{seat_label}"
        if cache.get(cache_key) == request.session.session_key:
            cache.delete(cache_key)
            return JsonResponse({'status': 'success', 'message': 'Đã nhả ghế.'})
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Không phải người giữ ghế.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ==============================================================================
# PHẦN 6: USER MANAGEMENT & ACCOUNT
# ==============================================================================

@login_required
def my_tickets(request):
    """
    TRANG 'VÉ CỦA TÔI'
    - Chức năng: Hiển thị lịch sử đặt vé.
    - Logic: Gom nhóm (Group) các vé rời rạc theo 'booking_code' để hiển thị thành từng đơn hàng.
    """
    all_tickets = Ticket.objects.filter(user=request.user).select_related(
        'showtime__movie', 'showtime__room'
    ).order_by('-booked_at', 'showtime')

    bookings = defaultdict(list)
    for ticket in all_tickets:
        key = ticket.booking_code if ticket.booking_code else f"legacy_{ticket.id}"
        bookings[key].append(ticket)
        
    processed_bookings = []
    for key, tickets_in_group in bookings.items():
        first = tickets_in_group[0]
        total = sum(t.price_paid for t in tickets_in_group)
        seats = [t.seat_label() for t in tickets_in_group]
        
        processed_bookings.append({
            'booking_code': first.booking_code,
            'showtime': first.showtime,
            'booked_at': first.booked_at,
            'seats': ", ".join(sorted(seats)),
            'total_price': total,
            'is_paid': first.is_paid, 
            'ticket_count': len(tickets_in_group)
        })
    
    # Sắp xếp đơn mới nhất lên đầu
    processed_bookings.sort(key=lambda b: b['booked_at'], reverse=True)
    return render(request, 'cinema_app/my_tickets.html', {'bookings': processed_bookings})

@login_required
def cancel_booking_view(request, booking_code):
    """Hủy đơn hàng đang chờ thanh toán."""
    if request.method == 'POST':
        Ticket.objects.filter(user=request.user, booking_code=booking_code, is_paid=False).delete()
        messages.success(request, f"Đã hủy đơn hàng {booking_code}.")
    return redirect('my_tickets')

@login_required
def retry_payment_view(request, booking_code):
    """Thanh toán lại cho đơn hàng bị lỗi/chưa thanh toán."""
    tickets = Ticket.objects.filter(user=request.user, booking_code=booking_code, is_paid=False)
    
    if not tickets.exists():
        messages.error(request, "Không tìm thấy đơn hàng.")
        return redirect('my_tickets')

    # Kiểm tra xem suất chiếu đã qua chưa
    if tickets.first().showtime.start_time < timezone.now():
        messages.error(request, "Đã quá giờ chiếu. Vé bị hủy.")
        tickets.delete()
        return redirect('my_tickets')

    total_price = sum(t.price_paid for t in tickets)
    payment_url = vnpay_helpers.get_vnpay_payment_url(request, booking_code, total_price)
    
    return redirect(payment_url)

def register_view(request):
    """Trang Đăng ký thành viên."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, full_name=form.cleaned_data.get('full_name', ''))
            messages.success(request, 'Đăng ký thành công.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'cinema_app/register.html', {'form': form})

def login_view(request):
    """Trang Đăng nhập."""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if is_staff_user(user):
                return redirect('manage_dashboard')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'cinema_app/login.html', {'form': form})

def logout_view(request):
    """Đăng xuất."""
    logout(request)
    return redirect('home')

@login_required
def account_view(request):
    """Trang Hồ sơ cá nhân (Điểm tích lũy, Hạng thành viên)."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    return render(request, 'cinema_app/account.html', {'profile': profile})

# ==============================================================================
# PHẦN 6.1: FOOD ORDER (ĐẶT ĐỒ ĂN)
# ==============================================================================

@login_required
def food_menu(request):
    """Trang Menu đồ ăn - Hiển thị danh sách đồ ăn"""
    foods = Food.objects.filter(is_available=True)
    categories = Food.CATEGORY_CHOICES
    
    # Lọc theo danh mục nếu có
    category = request.GET.get('category', '')
    if category:
        foods = foods.filter(category=category)
    
    return render(request, 'cinema_app/food_menu.html', {
        'foods': foods,
        'categories': categories,
        'selected_category': category
    })

@login_required
@require_POST
def add_to_food_cart(request):
    """API AJAX - Thêm đồ ăn vào giỏ"""
    try:
        data = json.loads(request.body)
        food_id = data.get('food_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity < 1:
            return JsonResponse({'status': 'error', 'message': 'Số lượng không hợp lệ'}, status=400)
        
        food = Food.objects.get(id=food_id, is_available=True)
        
        # Lưu vào session
        if 'food_cart' not in request.session:
            request.session['food_cart'] = {}
        
        cart = request.session['food_cart']
        food_key = str(food_id)
        
        if food_key in cart:
            cart[food_key]['quantity'] += quantity
        else:
            cart[food_key] = {
                'name': food.name,
                'price': str(food.price),
                'quantity': quantity
            }
        
        request.session.modified = True
        
        # Tính tổng giỏ
        total = sum(float(item['price']) * item['quantity'] for item in cart.values())
        
        return JsonResponse({
            'status': 'success',
            'message': f'Đã thêm {food.name}',
            'cart_total': total,
            'cart_count': len(cart)
        })
    except Food.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Đồ ăn không tồn tại'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def remove_food_from_cart(request):
    """API AJAX - Xóa đồ ăn khỏi giỏ"""
    try:
        data = json.loads(request.body)
        food_id = str(data.get('food_id'))
        
        if 'food_cart' in request.session:
            cart = request.session['food_cart']
            if food_id in cart:
                del cart[food_id]
                request.session.modified = True
                
                total = sum(float(item['price']) * item['quantity'] for item in cart.values())
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Đã xóa khỏi giỏ',
                    'cart_total': total,
                    'cart_count': len(cart)
                })
        
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy sản phẩm'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def view_food_cart(request):
    """Trang xem giỏ đồ ăn"""
    cart = request.session.get('food_cart', {})
    cart_items = []
    total = 0
    
    for food_id, item in cart.items():
        price = float(item['price'])
        quantity = item['quantity']
        subtotal = price * quantity
        cart_items.append({
            'food_id': food_id,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'cinema_app/food_cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def checkout_food(request):
    """Thanh toán đơn đặt đồ ăn"""
    cart = request.session.get('food_cart', {})
    
    if not cart:
        messages.error(request, 'Giỏ đồ ăn của bạn trống.')
        return redirect('food_menu')
    
    if request.method == 'POST':
        try:
            # Tính tổng tiền
            total_price = 0
            items_data = []
            
            for food_id, item in cart.items():
                food = Food.objects.get(id=int(food_id))
                quantity = item['quantity']
                price = float(item['price'])
                subtotal = price * quantity
                
                items_data.append({
                    'food': food,
                    'quantity': quantity,
                    'unit_price': price,
                    'subtotal': subtotal
                })
                total_price += subtotal
            
            # Tạo order code
            order_time = timezone.now()
            order_code = f"FOOD-{request.user.id}-{int(order_time.timestamp())}-{uuid.uuid4().hex[:4]}"
            
            with transaction.atomic():
                # Tạo đơn đặt đồ ăn
                food_order = FoodOrder.objects.create(
                    user=request.user,
                    showtime=None,  # Có thể thêm showtime nếu cần
                    order_code=order_code,
                    total_price=total_price,
                    is_paid=False
                )
                
                # Tạo chi tiết đơn
                for item in items_data:
                    FoodOrderItem.objects.create(
                        food_order=food_order,
                        food=item['food'],
                        quantity=item['quantity'],
                        unit_price=item['unit_price'],
                        subtotal=item['subtotal']
                    )
            
            # Xóa giỏ khỏi session
            del request.session['food_cart']
            request.session.modified = True
            
            # Tạo URL thanh toán VNPAY
            payment_url = vnpay_helpers.get_vnpay_payment_url(
                request=request,
                booking_code=order_code,
                total_price=total_price
            )
            
            messages.success(request, 'Tạo đơn đặt đồ ăn thành công. Vui lòng thanh toán.')
            return redirect(payment_url)
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('view_food_cart')
    
    # GET request - hiển thị trang xác nhận
    cart_items = []
    total = 0
    
    for food_id, item in cart.items():
        price = float(item['price'])
        quantity = item['quantity']
        subtotal = price * quantity
        cart_items.append({
            'food_id': food_id,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'cinema_app/food_checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def my_food_orders(request):
    """Trang lịch sử đặt đồ ăn của tôi"""
    orders = FoodOrder.objects.filter(user=request.user).prefetch_related('items__food').order_by('-ordered_at')
    
    processed_orders = []
    for order in orders:
        items = []
        for item in order.items.all():
            items.append({
                'name': item.food.name if item.food else 'N/A',
                'quantity': item.quantity,
                'subtotal': item.subtotal
            })
        
        processed_orders.append({
            'order': order,
            'items': items
        })
    
    return render(request, 'cinema_app/my_food_orders.html', {
        'orders': processed_orders
    })

# ==============================================================================
# PHẦN 7: STAFF MANAGEMENT (QUẢN TRỊ VIÊN)
# ==============================================================================

@user_passes_test(is_staff_user)
def manage_dashboard(request):
    """
    DASHBOARD QUẢN TRỊ (CƠ BẢN)
    - Hiển thị thống kê nhanh: Số lượng phim, rạp, vé bán ra, tổng doanh thu.
    """
    stats = {
        'movies': Movie.objects.count(),
        'rooms': CinemaRoom.objects.count(),
        'showtimes': ShowTime.objects.count(),
        'tickets': Ticket.objects.filter(is_paid=True).count(),
        'revenue': Ticket.objects.filter(is_paid=True).aggregate(total=Sum('price_paid'))['total'] or 0,
    }
    return render(request, 'cinema_app/manage/dashboard.html', {'stats': stats})

@user_passes_test(is_staff_user)
def manage_analytics(request):
    """
    DASHBOARD PHÂN TÍCH DỮ LIỆU NÂNG CAO (DATA ANALYTICS)
    - Chức năng: Tính toán KPI và chuẩn bị dữ liệu vẽ biểu đồ.
    - Công nghệ: Django Aggregation, Date Truncation, Python Logic xử lý Matrix.
    """
    # 1. Lấy khoảng thời gian lọc (Mặc định 30 ngày)
    end_date_str = request.GET.get('end_date')
    start_date_str = request.GET.get('start_date')
    today = timezone.now().date()
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = today

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = end_date - timedelta(days=29)

    start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_dt = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    # --- QUERY DATASET ---
    tickets_qs = Ticket.objects.filter(is_paid=True, booked_at__range=(start_dt, end_dt))

    # 2. TÍNH KPIs (Doanh thu, Giá vé TB, Tỷ lệ lấp đầy)
    total_revenue = tickets_qs.aggregate(total=Sum('price_paid'))['total'] or 0
    total_tickets = tickets_qs.count()
    avg_ticket_price = (total_revenue / total_tickets) if total_tickets > 0 else 0
    
    # Tính Occupancy Rate (Số vé / Tổng ghế của các suất chiếu đã qua)
    showtimes_in_period = ShowTime.objects.filter(start_time__range=(start_dt, end_dt))
    total_capacity = showtimes_in_period.aggregate(cap=Sum(F('room__rows') * F('room__cols')))['cap'] or 0
    occupancy_rate = (total_tickets / total_capacity * 100) if total_capacity > 0 else 0

    kpis = {
        'revenue': total_revenue,
        'tickets': total_tickets,
        'avg_price': avg_ticket_price,
        'occupancy': round(occupancy_rate, 1),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }

    # 3. DỮ LIỆU BIỂU ĐỒ DOANH THU (Line Chart)
    # Gom nhóm theo ngày
    revenue_by_date = tickets_qs.annotate(date=TruncDate('booked_at')).values('date').annotate(daily_revenue=Sum('price_paid')).order_by('date')
    
    chart_dates = []
    chart_revenues = []
    temp_date = start_date
    revenue_map = {item['date']: item['daily_revenue'] for item in revenue_by_date}
    
    # Fill 0 cho những ngày không có doanh thu
    while temp_date <= end_date:
        chart_dates.append(temp_date.strftime('%d/%m'))
        chart_revenues.append(float(revenue_map.get(temp_date, 0)))
        temp_date += timedelta(days=1)

    line_chart_data = {'labels': chart_dates, 'data': chart_revenues}

    # 4. DỮ LIỆU TOP 5 PHIM (Bar Chart)
    top_movies = tickets_qs.values('showtime__movie__title').annotate(total=Sum('price_paid')).order_by('-total')[:5]
    bar_chart_data = {
        'labels': [item['showtime__movie__title'] for item in top_movies],
        'data': [float(item['total']) for item in top_movies]
    }

    # 5. DỮ LIỆU TỶ TRỌNG PHÒNG CHIẾU (Doughnut Chart)
    tickets_by_room = tickets_qs.values('showtime__room__name').annotate(count=Count('id')).order_by('-count')
    pie_chart_data = {
        'labels': [item['showtime__room__name'] for item in tickets_by_room],
        'data': [item['count'] for item in tickets_by_room]
    }

    # 6. DỮ LIỆU HEATMAP (Khung giờ & Thứ trong tuần)
    heatmap_data = tickets_qs.annotate(
        weekday=ExtractWeekDay('booked_at'),
        hour=ExtractHour('booked_at')
    ).values('weekday', 'hour').annotate(count=Count('id'))

    heatmap_matrix = [[0]*16 for _ in range(7)]
    max_val = 0
    
    for item in heatmap_data:
        # Convert Django WeekDay (1=Sun) -> Python index (6=Sun)
        wd_idx = 6 if item['weekday'] == 1 else item['weekday'] - 2
        hour = item['hour']
        if 8 <= hour <= 23:
            h_idx = hour - 8
            count = item['count']
            heatmap_matrix[wd_idx][h_idx] = count
            if count > max_val: max_val = count

    return render(request, 'cinema_app/manage/analytics.html', {
        'kpis': kpis,
        'line_chart': json.dumps(line_chart_data),
        'bar_chart': json.dumps(bar_chart_data),
        'pie_chart': json.dumps(pie_chart_data),
        'heatmap': heatmap_matrix,
        'max_val': max_val,
        'hours_label': range(8, 24)
    })

# --- Các hàm Quản lý CRUD (Phim, Phòng, Suất chiếu, User) ---
# Logic chung: Sử dụng ModelForm để validate và lưu dữ liệu.

@user_passes_test(is_staff_user)
def manage_movies(request):
    """Quản lý danh sách phim."""
    form = MovieForm()
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'cinema_app/manage/manage_movies.html', {'movies': movies, 'form': form})

@user_passes_test(is_staff_user)
def manage_movie_create(request):
    """Thêm phim mới."""
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm phim.')
            return redirect('manage_movies')
    else:
        form = MovieForm()
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'cinema_app/manage/manage_movies.html', {'form': form, 'create': True, 'movies': movies})

@user_passes_test(is_staff_user)
def manage_movie_edit(request, pk):
    """Sửa thông tin phim."""
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật phim.')
            return redirect('manage_movies')
    else:
        form = MovieForm(instance=movie)
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'cinema_app/manage/manage_movies.html', {'form': form, 'edit': True, 'movies': movies, 'editing': movie})

@user_passes_test(is_staff_user)
def manage_movie_delete(request, pk):
    """Xóa phim."""
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.info(request, 'Đã xóa phim.')
    return redirect('manage_movies')

# (Tương tự cho Manage Rooms, Showtimes, Promotions...)
@user_passes_test(is_staff_user)
def manage_rooms(request):
    form = RoomForm()
    rooms = CinemaRoom.objects.all().order_by('name')
    return render(request, 'cinema_app/manage/manage_rooms.html', {'rooms': rooms, 'form': form})
@user_passes_test(is_staff_user)
def manage_room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm phòng chiếu.')
            return redirect('manage_rooms')
    else:
        form = RoomForm()
    rooms = CinemaRoom.objects.all().order_by('name')
    return render(request, 'cinema_app/manage/manage_rooms.html', {'form': form, 'create': True, 'rooms': rooms})
@user_passes_test(is_staff_user)
def manage_room_edit(request, pk):
    room = get_object_or_404(CinemaRoom, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật phòng chiếu.')
            return redirect('manage_rooms')
    else:
        form = RoomForm(instance=room)
    rooms = CinemaRoom.objects.all().order_by('name')
    return render(request, 'cinema_app/manage/manage_rooms.html', {'form': form, 'edit': True, 'rooms': rooms, 'editing': room})
@user_passes_test(is_staff_user)
def manage_room_delete(request, pk):
    room = get_object_or_404(CinemaRoom, pk=pk)
    room.delete()
    messages.info(request, 'Đã xóa phòng chiếu.')
    return redirect('manage_rooms')
@user_passes_test(is_staff_user)
def manage_showtimes(request):
    form = ShowTimeForm()
    sts = ShowTime.objects.select_related('movie', 'room').all().order_by('-start_time')
    return render(request, 'cinema_app/manage/manage_showtimes.html', {'showtimes': sts, 'form': form})
@user_passes_test(is_staff_user)
def manage_showtime_create(request):
    if request.method == 'POST':
        form = ShowTimeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm suất chiếu.')
            return redirect('manage_showtimes')
    else:
        form = ShowTimeForm()
    sts = ShowTime.objects.select_related('movie', 'room').all().order_by('-start_time')
    return render(request, 'cinema_app/manage/manage_showtimes.html', {'form': form, 'create': True, 'showtimes': sts})
@user_passes_test(is_staff_user)
def manage_showtime_edit(request, pk):
    st = get_object_or_404(ShowTime, pk=pk)
    if request.method == 'POST':
        form = ShowTimeForm(request.POST, instance=st)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật suất chiếu.')
            return redirect('manage_showtimes')
    else:
        form = ShowTimeForm(instance=st)
    sts = ShowTime.objects.select_related('movie', 'room').all().order_by('-start_time')
    return render(request, 'cinema_app/manage/manage_showtimes.html', {'form': form, 'edit': True, 'showtimes': sts, 'editing': st})
@user_passes_test(is_staff_user)
def manage_showtime_delete(request, pk):
    st = get_object_or_404(ShowTime, pk=pk)
    st.delete()
    messages.info(request, 'Đã xóa suất chiếu.')
    return redirect('manage_showtimes')
@user_passes_test(is_staff_user)
def manage_promotions(request):
    form = PromotionForm()
    promotions = Promotion.objects.all().order_by('-valid_until')
    return render(request, 'cinema_app/manage/manage_promotions.html', {'promotions': promotions, 'form': form})
@user_passes_test(is_staff_user)
def manage_promotion_create(request):
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm mã khuyến mãi.')
            return redirect('manage_promotions')
    else:
        form = PromotionForm()
    promotions = Promotion.objects.all().order_by('-valid_until')
    return render(request, 'cinema_app/manage/manage_promotions.html', {'form': form, 'create': True, 'promotions': promotions})
@user_passes_test(is_staff_user)
def manage_promotion_edit(request, pk):
    promo = get_object_or_404(Promotion, pk=pk)
    if request.method == 'POST':
        form = PromotionForm(request.POST, instance=promo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật khuyến mãi.')
            return redirect('manage_promotions')
    else:
        form = PromotionForm(instance=promo)
    promotions = Promotion.objects.all().order_by('-valid_until')
    return render(request, 'cinema_app/manage/manage_promotions.html', {'form': form, 'edit': True, 'promotions': promotions, 'editing': promo})
@user_passes_test(is_staff_user)
def manage_promotion_delete(request, pk):
    promo = get_object_or_404(Promotion, pk=pk)
    promo.delete()
    messages.info(request, 'Đã xóa khuyến mãi.')
    return redirect('manage_promotions')
@user_passes_test(is_staff_user)
def manage_reports(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    qs = Ticket.objects.all()
    if start:
        qs = qs.filter(booked_at__date__gte=start)
    if end:
        qs = qs.filter(booked_at__date__lte=end)
    revenue = qs.aggregate(total=Sum('price_paid'))['total'] or 0
    count = qs.count()
    by_movie = qs.values('showtime__movie__title').annotate(tickets=Count('id'), money=Sum('price_paid')).order_by('-money')
    return render(request, 'cinema_app/manage/manage_reports.html', {'revenue': revenue, 'count': count, 'by_movie': by_movie, 'start': start, 'end': end})

@user_passes_test(is_staff_user)
def manage_users(request):
    """
    QUẢN LÝ NGƯỜI DÙNG (ADMIN)
    - Chức năng: Xem danh sách, thêm, sửa, xóa người dùng.
    - Logic: Lấy danh sách user kèm theo Profile (select_related).
    """
    form = ManageUserForm()
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'cinema_app/manage/manage_users.html', {'users': users, 'form': form})

@user_passes_test(is_staff_user)
def manage_user_create(request):
    """Thêm người dùng mới (bao gồm cả nhân viên) từ trang quản trị."""
    if request.method == 'POST':
        form = ManageUserForm(request.POST)
        if form.is_valid():
            try:
                # Sử dụng Transaction để đảm bảo User và Profile cùng được tạo
                with transaction.atomic():
                    # 1. Tạo User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password']
                    )
                    user.is_active = form.cleaned_data['is_active']
                    if form.cleaned_data['role'] == 'STAFF':
                        user.is_staff = True
                    user.save()

                    # 2. Tạo Profile
                    Profile.objects.create(
                        user=user,
                        full_name=form.cleaned_data['full_name'],
                        phone=form.cleaned_data['phone'],
                        role=form.cleaned_data['role']
                    )
                    messages.success(request, f'Đã thêm người dùng {user.username}.')
                    return redirect('manage_users')
            except IntegrityError:
                messages.error(request, 'Tên tài khoản đã tồn tại.')
        else:
             messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    return redirect('manage_users')

@user_passes_test(is_staff_user)
def manage_user_edit(request, pk):
    """Sửa thông tin người dùng."""
    user = get_object_or_404(User, pk=pk)
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        form = ManageUserForm(request.POST, instance=user, profile_instance=profile)
        if form.is_valid():
            u = form.save(commit=False)
            new_pass = form.cleaned_data.get('password')
            if new_pass:
                u.set_password(new_pass)
            
            role = form.cleaned_data['role']
            if role == 'STAFF':
                u.is_staff = True
            else:
                u.is_staff = False
            u.save()

            profile.full_name = form.cleaned_data['full_name']
            profile.phone = form.cleaned_data['phone']
            profile.role = role
            profile.save()

            messages.success(request, 'Đã cập nhật thông tin người dùng.')
            return redirect('manage_users')
    else:
        form = ManageUserForm(instance=user, profile_instance=profile)
    
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'cinema_app/manage/manage_users.html', {'form': form, 'edit': True, 'users': users, 'editing': user})

@user_passes_test(is_staff_user)
def manage_user_delete(request, pk):
    """Xóa người dùng (Không cho phép xóa Admin tối cao)."""
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, 'Không thể xóa Superuser (Admin tối cao).')
    elif user == request.user:
        messages.error(request, 'Bạn không thể tự xóa chính mình.')
    else:
        user.delete()
        messages.success(request, 'Đã xóa người dùng.')
    return redirect('manage_users')

# ==============================================================================
# PHẦN 7.1: STAFF MANAGEMENT - FOOD (QUẢN LÝ ĐỒ ĂN)
# ==============================================================================

@user_passes_test(is_staff_user)
def manage_foods(request):
    """Quản lý danh sách đồ ăn."""
    form = FoodManageForm()
    foods = Food.objects.all().order_by('category', 'name')
    return render(request, 'cinema_app/manage/manage_foods.html', {'foods': foods, 'form': form})

@user_passes_test(is_staff_user)
def manage_food_create(request):
    """Thêm đồ ăn mới."""
    if request.method == 'POST':
        form = FoodManageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm đồ ăn.')
            return redirect('manage_foods')
    else:
        form = FoodManageForm()
    foods = Food.objects.all().order_by('category', 'name')
    return render(request, 'cinema_app/manage/manage_foods.html', {'form': form, 'create': True, 'foods': foods})

@user_passes_test(is_staff_user)
def manage_food_edit(request, pk):
    """Sửa thông tin đồ ăn."""
    food = get_object_or_404(Food, pk=pk)
    if request.method == 'POST':
        form = FoodManageForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật đồ ăn.')
            return redirect('manage_foods')
    else:
        form = FoodManageForm(instance=food)
    foods = Food.objects.all().order_by('category', 'name')
    return render(request, 'cinema_app/manage/manage_foods.html', {'form': form, 'edit': True, 'foods': foods, 'editing': food})

@user_passes_test(is_staff_user)
def manage_food_delete(request, pk):
    """Xóa đồ ăn."""
    food = get_object_or_404(Food, pk=pk)
    food.delete()
    messages.info(request, 'Đã xóa đồ ăn.')
    return redirect('manage_foods')

@user_passes_test(is_staff_user)
def manage_food_orders(request):
    """Quản lý các đơn đặt đồ ăn."""
    orders = FoodOrder.objects.select_related('user').prefetch_related('items__food').order_by('-ordered_at')
    
    processed_orders = []
    for order in orders:
        items = []
        for item in order.items.all():
            items.append({
                'name': item.food.name if item.food else 'N/A',
                'quantity': item.quantity,
                'subtotal': item.subtotal
            })
        
        processed_orders.append({
            'order': order,
            'items': items,
            'item_count': len(items)
        })
    
    return render(request, 'cinema_app/manage/manage_food_orders.html', {
        'orders': processed_orders
    })
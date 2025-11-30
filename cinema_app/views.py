# Đường dẫn: cinema_app/views.py
# Tìm các dòng import từ django.contrib.auth...
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

# --- THÊM DÒNG NÀY VÀO ---
from django.contrib.auth.models import User
# -------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction, IntegrityError
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Case, When, Q
from django.db.models.functions import TruncDate, ExtractWeekDay, ExtractHour
from django.utils import timezone
from datetime import date, datetime, timedelta
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import uuid
from . import vnpay_helpers, utils

from .models import Movie, CinemaRoom, ShowTime, Ticket, Promotion, Profile, Review
# Tìm đoạn này ở gần đầu file và sửa lại:

from .forms import (
    RegisterForm, LoginForm, MovieForm, RoomForm, ShowTimeForm, 
    PromotionForm, BookingForm, ReviewForm, ManageUserForm  # <--- Thêm ManageUserForm vào đây
)

# --- Helpers ---
def is_staff_user(user):
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 'STAFF' or user.is_staff
    except Profile.DoesNotExist:
        return user.is_staff

# ... (Giữ nguyên các import cũ)
# Thêm import Q nếu chưa có (để tìm kiếm nâng cao nếu cần, nhưng ở đây dùng filter cơ bản cũng được)
# ... (Giữ nguyên các import cũ)
# Thêm import Q nếu chưa có (để tìm kiếm nâng cao nếu cần, nhưng ở đây dùng filter cơ bản cũng được)
from django.db.models import Q 

# --- Helper Function: Lấy danh sách thể loại ---
def get_all_genres():
    """
    Lấy tất cả thể loại từ DB, tách các chuỗi dạng 'Hành động, Hài' thành list duy nhất.
    """
    # Lấy tất cả giá trị cột genre
    raw_genres = Movie.objects.values_list('genre', flat=True).distinct()
    unique_genres = set()
    
    for g_str in raw_genres:
        if g_str:
            # Tách dấu phẩy (nếu phim có nhiều thể loại) và xóa khoảng trắng thừa
            parts = [x.strip() for x in g_str.split(',')]
            for p in parts:
                if p: unique_genres.add(p)
                
    return sorted(list(unique_genres))

# --- CẬP NHẬT VIEW HOME ---
def home(request):
    today = timezone.localdate()
    
    # 1. Lấy tham số từ URL
    q = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()

    # 2. Query cơ bản
    now_showing_movies = Movie.objects.filter(
        release_date__lte=today,
        showtime__start_time__gte=timezone.now()
    ).distinct().order_by('-release_date')
    
    coming_soon_movies = Movie.objects.filter(
        release_date__gt=today
    ).order_by('release_date')

    # 3. Áp dụng bộ lọc (Search + Genre)
    if q:
        now_showing_movies = now_showing_movies.filter(title__icontains=q)
        coming_soon_movies = coming_soon_movies.filter(title__icontains=q)
    
    if selected_genre:
        now_showing_movies = now_showing_movies.filter(genre__icontains=selected_genre)
        coming_soon_movies = coming_soon_movies.filter(genre__icontains=selected_genre)

    # Lấy lịch chiếu (chỉ lọc theo genre nếu có, không lọc theo tên phim để tránh list trống trơn)
   # ... (các đoạn trên giữ nguyên)

    # --- SỬA ĐOẠN NÀY ---
    # 1. Tạo QuerySet cơ bản (chưa cắt [:12])
    upcoming_showtimes_qs = ShowTime.objects.filter(
        start_time__gte=timezone.now()
    ).select_related('movie', 'room').order_by('start_time')

    # 2. Áp dụng bộ lọc (nếu có)
    if selected_genre:
        upcoming_showtimes_qs = upcoming_showtimes_qs.filter(movie__genre__icontains=selected_genre)

    # 3. Sau khi lọc xong mới được cắt (Slice) lấy 12 bản ghi đầu tiên
    upcoming_showtimes = upcoming_showtimes_qs[:12]

    return render(request, 'cinema_app/home.html', {
        # ... (giữ nguyên context)
        'now_showing_movies': now_showing_movies,
        'coming_soon_movies': coming_soon_movies,
        'upcoming_showtimes': upcoming_showtimes,
        'genres': get_all_genres(),
        'selected_genre': selected_genre,
        'q': q,
    })
# --- CẬP NHẬT VIEW MOVIE_LIST ---
def movie_list(request):
    today = timezone.localdate()
    
    # 1. Lấy tham số
    q = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()
    
    # 2. Query cơ bản
    now_showing_movies = Movie.objects.filter(
        release_date__lte=today
    ).distinct().order_by('-release_date')
    
    coming_soon_movies = Movie.objects.filter(
        release_date__gt=today
    ).order_by('release_date')

    # 3. Áp dụng bộ lọc
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

# ... (Các hàm khác giữ nguyên)

# ... (CÁC HÀM KHÁC GIỮ NGUYÊN KHÔNG ĐỔI) ...
# (Copy phần còn lại của views.py cũ vào đây từ dòng movie_detail trở đi)
# Để ngắn gọn, bạn giữ nguyên các hàm movie_detail, schedule_view... như cũ nhé.
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes = ShowTime.objects.filter(
        movie=movie, 
        start_time__gte=timezone.now()
    ).select_related('room').order_by('start_time')

    reviews = movie.reviews.all()
    user_can_review = False
    review_form = None

    if request.user.is_authenticated:
        has_paid_ticket = Ticket.objects.filter(
            user=request.user, 
            showtime__movie=movie, 
            is_paid=True
        ).exists()
        
        has_reviewed = Review.objects.filter(user=request.user, movie=movie).exists()
        
        if has_paid_ticket and not has_reviewed:
            user_can_review = True
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
    movie_id = request.GET.get('movie')
    selected_date_str = request.GET.get('date')

    if not selected_date_str:
        selected_date = timezone.localdate()
        selected_date_str = selected_date.isoformat()
    else:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.localdate()
            selected_date_str = selected_date.isoformat()

    start_of_day_naive = datetime.combine(selected_date, datetime.min.time())
    start_of_day_aware = timezone.make_aware(start_of_day_naive)
    
    if selected_date == timezone.localdate():
        start_of_day_aware = timezone.now()

    end_of_day_aware = start_of_day_aware.replace(hour=23, minute=59, second=59)

    qs = ShowTime.objects.filter(
        start_time__range=(start_of_day_aware, end_of_day_aware)
    ).select_related('movie', 'room').order_by('movie__title', 'start_time')

    if movie_id:
        qs = qs.filter(movie_id=movie_id)

    movies_with_showtimes_today = Movie.objects.filter(
        showtime__start_time__range=(start_of_day_aware, end_of_day_aware)
    ).distinct().order_by('title')

    return render(request, 'cinema_app/schedule.html', {
        'showtimes': qs, 
        'movies': movies_with_showtimes_today, 
        'selected_movie': movie_id, 
        'selected_date': selected_date_str 
    })

@login_required
def booking_view(request, showtime_id):
    showtime = get_object_or_404(ShowTime, pk=showtime_id)
    room = showtime.room
    
    taken_seats = set(Ticket.objects.filter(showtime=showtime, is_paid=True).values_list('seat_row', 'seat_number'))
    
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

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data['seats']
            promo_code = form.cleaned_data.get('promo_code', '').strip()
            
            seats_taken_or_locked = []
            valid_seats = []
            
            for seat in seats:
                seat = seat.strip()
                if not seat: continue
                try:
                    seat_row = ''.join([c for c in seat if c.isalpha()]).upper()
                    seat_number_str = ''.join([c for c in seat if c.isdigit()])
                    seat_number = int(seat_number_str)
                    seat_tuple = (seat_row, seat_number)

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
                messages.error(request, f"Rất tiếc! Ghế {', '.join(seats_taken_or_locked)} đã có người khác chọn. Vui lòng chọn lại.")
                return redirect('booking', showtime_id=showtime.id)
            if not valid_seats:
                messages.error(request, "Bạn chưa chọn ghế hợp lệ nào.")
                return redirect('booking', showtime_id=showtime.id)

            discount = 0
            if promo_code:
                promo = Promotion.objects.filter(code__iexact=promo_code, is_active=True, valid_until__gte=today).first()
                if not promo:
                    messages.warning(request, 'Mã khuyến mãi không hợp lệ hoặc đã hết hạn.')
                else:
                    discount = promo.discount_percent

            num_seats = len(valid_seats)
            base_price_per_seat = showtime.base_price
            price_paid_per_seat = (base_price_per_seat * (100 - discount) / 100)
            total_price = price_paid_per_seat * num_seats
            booked_time = timezone.now()
            booking_code = f"{request.user.id}-{int(booked_time.timestamp())}-{uuid.uuid4().hex[:4]}"

            try:
                with transaction.atomic():
                    for seat_info in valid_seats:
                        Ticket.objects.create(
                            user=request.user,
                            showtime=showtime,
                            booking_code=booking_code,
                            seat_row=seat_info['row'],
                            seat_number=seat_info['number'],
                            price_paid=price_paid_per_seat,
                            is_paid=False, 
                            booked_at=booked_time 
                        )
                        cache_key = f"seat_{showtime.id}_{seat_info['label']}"
                        cache.delete(cache_key)
                    
                    payment_url = vnpay_helpers.get_vnpay_payment_url(
                        request=request,
                        booking_code=booking_code,
                        total_price=total_price
                    )
                    
                    return redirect(payment_url)

            except IntegrityError:
                messages.error(request, 'Lỗi: Ghế bạn chọn vừa có người khác đặt. Vui lòng thử lại.')
                return redirect('booking', showtime_id=showtime.id)
    else:
        form = BookingForm()

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
                status = 'selected'
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
    input_data = request.GET.dict() 
    if not input_data:
        messages.error(request, "Lỗi: Không nhận được dữ liệu trả về từ VNPAY.")
        return redirect('my_tickets')

    is_valid, message = vnpay_helpers.verify_vnpay_return(input_data)
    booking_code = input_data.get('vnp_TxnRef')

    if not is_valid:
        if booking_code:
            Ticket.objects.filter(booking_code=booking_code, is_paid=False).delete()
        messages.error(request, f"Lỗi thanh toán: {message}")
        return redirect('my_tickets')

    if message == "Thanh toán thành công":
        try:
            tickets_to_pay = Ticket.objects.filter(booking_code=booking_code, is_paid=False)
            
            if not tickets_to_pay.exists():
                if Ticket.objects.filter(booking_code=booking_code, is_paid=True).exists():
                    messages.warning(request, "Đơn hàng này đã được xử lý trước đó.")
                    return redirect('my_tickets')
                else:
                    messages.error(request, "Không tìm thấy vé để xử lý.")
                    return redirect('my_tickets')

            total_amount = tickets_to_pay.aggregate(Sum('price_paid'))['price_paid__sum'] or 0
            points_earned = int(total_amount / 1000)

            with transaction.atomic():
                tickets_to_pay.update(is_paid=True)
                try:
                    profile = request.user.profile
                    profile.points += points_earned
                    profile.update_membership()
                    profile.save()
                    messages.success(request, f"Thanh toán thành công! Bạn được cộng {points_earned} điểm.")
                except Profile.DoesNotExist:
                    pass 
            
            user_email = request.user.email
            if user_email:
                try:
                    validate_email(user_email)
                    tickets_paid = Ticket.objects.filter(booking_code=booking_code)
                    utils.send_eticket_email(request.user, booking_code, tickets_paid, total_amount)
                    messages.info(request, f"Vé điện tử đã được gửi đến {user_email}.")
                except Exception as e:
                    print(f"Lỗi gửi mail: {e}")
                    messages.warning(request, "Không thể gửi email vé do lỗi hệ thống.")
            else:
                messages.warning(request, "Bạn chưa cập nhật email nên không thể nhận vé điện tử.")

            return redirect('my_tickets')
                
        except Exception as e:
            messages.error(request, f"Lỗi nghiêm trọng: {str(e)}")
            return redirect('my_tickets')
    else:
        if booking_code:
            Ticket.objects.filter(booking_code=booking_code, is_paid=False).delete()
        messages.error(request, f"Giao dịch thất bại: {message}")
        return redirect('my_tickets')

@login_required
@require_POST
def lock_seat(request):
    try:
        if not request.session.session_key: request.session.create()
        data = json.loads(request.body)
        showtime_id = data.get('showtime_id')
        seat_label = data.get('seat_label')
        if not showtime_id or not seat_label:
            return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin.'}, status=400)
        cache_key = f"seat_{showtime_id}_{seat_label}"
        is_locked = cache.add(cache_key, request.session.session_key, timeout=600)
        if is_locked:
            return JsonResponse({'status': 'success', 'message': 'Giữ ghế thành công.'})
        else:
            if cache.get(cache_key) == request.session.session_key:
                 return JsonResponse({'status': 'success', 'message': 'Bạn đã giữ ghế này.'})
            return JsonResponse({'status': 'error', 'message': 'Ghế đã bị người khác chọn.'}, status=409)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def release_seat(request):
    try:
        data = json.loads(request.body)
        showtime_id = data.get('showtime_id')
        seat_label = data.get('seat_label')
        if not showtime_id or not seat_label:
            return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin.'}, status=400)
        cache_key = f"seat_{showtime_id}_{seat_label}"
        if cache.get(cache_key) == request.session.session_key:
            cache.delete(cache_key)
            return JsonResponse({'status': 'success', 'message': 'Đã nhả ghế.'})
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Không phải người giữ ghế.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def my_tickets(request):
    all_tickets = Ticket.objects.filter(user=request.user).select_related(
        'showtime__movie', 'showtime__room'
    ).order_by('-booked_at', 'showtime')

    bookings = defaultdict(list)
    for ticket in all_tickets:
        if ticket.booking_code:
            booking_key = ticket.booking_code
        else:
            booking_key = f"legacy_{ticket.id}" 
        
        bookings[booking_key].append(ticket)
        
    processed_bookings = []
    for key, tickets_in_group in bookings.items():
        first_ticket = tickets_in_group[0]
        total_price = sum(t.price_paid for t in tickets_in_group)
        seat_labels = [t.seat_label() for t in tickets_in_group]
        
        processed_bookings.append({
            'booking_code': first_ticket.booking_code,
            'showtime': first_ticket.showtime,
            'booked_at': first_ticket.booked_at,
            'seats': ", ".join(sorted(seat_labels)),
            'total_price': total_price,
            'is_paid': first_ticket.is_paid, 
            'ticket_count': len(tickets_in_group)
        })
    processed_bookings.sort(key=lambda b: b['booked_at'], reverse=True)
    return render(request, 'cinema_app/my_tickets.html', {
        'bookings': processed_bookings
    })

@login_required
def cancel_booking_view(request, booking_code):
    if request.method == 'POST':
        tickets_to_cancel = Ticket.objects.filter(
            user=request.user,
            booking_code=booking_code,
            is_paid=False
        )
        
        if tickets_to_cancel.exists():
            tickets_to_cancel.delete()
            messages.success(request, f"Đã hủy đơn hàng {booking_code} đang chờ thanh toán.")
        else:
            messages.error(request, "Không tìm thấy đơn hàng chờ hoặc đơn hàng đã được thanh toán.")
            
    return redirect('my_tickets')

@login_required
def retry_payment_view(request, booking_code):
    tickets = Ticket.objects.filter(
        user=request.user,
        booking_code=booking_code,
        is_paid=False
    )
    
    if not tickets.exists():
        messages.error(request, "Không tìm thấy đơn hàng chờ thanh toán này.")
        return redirect('my_tickets')

    first_ticket = tickets.first()
    if first_ticket.showtime.start_time < timezone.now():
        messages.error(request, "Đã quá giờ chiếu. Không thể thanh toán.")
        tickets.delete()
        return redirect('my_tickets')

    total_price = sum(t.price_paid for t in tickets)
    
    payment_url = vnpay_helpers.get_vnpay_payment_url(
        request=request,
        booking_code=booking_code,
        total_price=total_price
    )
    
    return redirect(payment_url)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user, 
                full_name=form.cleaned_data.get('full_name', '')
            )
            messages.success(request, 'Đăng ký thành công. Bạn có thể đăng nhập ngay.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'cinema_app/register.html', {'form': form})

def login_view(request):
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
    logout(request)
    return redirect('home')

@login_required
def account_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    return render(request, 'cinema_app/account.html', {'profile': profile})

# --- Views Quản lý (Staff) ---

@user_passes_test(is_staff_user)
def manage_dashboard(request):
    stats = {
        'movies': Movie.objects.count(),
        'rooms': CinemaRoom.objects.count(),
        'showtimes': ShowTime.objects.count(),
        'tickets': Ticket.objects.filter(is_paid=True).count(),
        'revenue': Ticket.objects.filter(is_paid=True).aggregate(total=Sum('price_paid'))['total'] or 0,
    }
    return render(request, 'cinema_app/manage/dashboard.html', {'stats': stats})

# --- VIEW MỚI: ADVANCED ANALYTICS ---
@user_passes_test(is_staff_user)
def manage_analytics(request):
    # 1. Lấy khoảng thời gian từ bộ lọc (Mặc định: 30 ngày gần nhất)
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

    # Tạo range datetime (bao gồm cả ngày cuối cùng)
    start_dt = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_dt = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))

    # --- QUERY DATASET CHUNG (Vé đã thanh toán trong khoảng thời gian) ---
    tickets_qs = Ticket.objects.filter(
        is_paid=True, 
        booked_at__range=(start_dt, end_dt)
    )

    # 2. TÍNH TOÁN KPIs
    total_revenue = tickets_qs.aggregate(total=Sum('price_paid'))['total'] or 0
    total_tickets = tickets_qs.count()
    avg_ticket_price = (total_revenue / total_tickets) if total_tickets > 0 else 0
    
    # Tính Occupancy Rate (Tỷ lệ lấp đầy)
    # Cần: Tổng ghế của các suất chiếu ĐÃ DIỄN RA trong khoảng thời gian này
    showtimes_in_period = ShowTime.objects.filter(
        start_time__range=(start_dt, end_dt)
    )
    
    # Tổng dung lượng ghế (Total Capacity)
    # Logic: Sum(rows * cols) của tất cả showtime
    total_capacity = showtimes_in_period.aggregate(
        cap=Sum(F('room__rows') * F('room__cols'))
    )['cap'] or 0
    
    occupancy_rate = (total_tickets / total_capacity * 100) if total_capacity > 0 else 0

    kpis = {
        'revenue': total_revenue,
        'tickets': total_tickets,
        'avg_price': avg_ticket_price,
        'occupancy': round(occupancy_rate, 1),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }

    # 3. CHART 1: DOANH THU THEO NGÀY (LINE CHART)
    revenue_by_date = tickets_qs.annotate(
        date=TruncDate('booked_at')
    ).values('date').annotate(
        daily_revenue=Sum('price_paid')
    ).order_by('date')

    # Chuẩn bị data cho Chart.js (Cần điền 0 cho những ngày không có doanh thu)
    chart_dates = []
    chart_revenues = []
    
    temp_date = start_date
    revenue_map = {item['date']: item['daily_revenue'] for item in revenue_by_date}
    
    while temp_date <= end_date:
        chart_dates.append(temp_date.strftime('%d/%m'))
        chart_revenues.append(float(revenue_map.get(temp_date, 0)))
        temp_date += timedelta(days=1)

    line_chart_data = {
        'labels': chart_dates,
        'data': chart_revenues
    }

    # 4. CHART 2: TOP 5 PHIM DOANH THU CAO NHẤT (BAR CHART)
    top_movies = tickets_qs.values(
        'showtime__movie__title'
    ).annotate(
        total=Sum('price_paid')
    ).order_by('-total')[:5]

    bar_chart_data = {
        'labels': [item['showtime__movie__title'] for item in top_movies],
        'data': [float(item['total']) for item in top_movies]
    }

    # 5. CHART 3: TỶ TRỌNG PHÒNG CHIẾU (DOUGHNUT CHART)
    # Tỷ lệ vé bán ra theo từng phòng
    tickets_by_room = tickets_qs.values(
        'showtime__room__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    pie_chart_data = {
        'labels': [item['showtime__room__name'] for item in tickets_by_room],
        'data': [item['count'] for item in tickets_by_room]
    }

    # 6. HEATMAP: KHUNG GIỜ ĐÔNG KHÁCH (TABLE HEATMAP)
    # Group by WeekDay (2-8) và Hour (0-23)
    # Django: Sunday=1, Saturday=7. Ta sẽ map lại cho dễ hiểu: Mon=0 -> Sun=6
    heatmap_data = tickets_qs.annotate(
        weekday=ExtractWeekDay('booked_at'), # 1=Sun, 2=Mon...
        hour=ExtractHour('booked_at')
    ).values('weekday', 'hour').annotate(
        count=Count('id')
    )

    # Tạo ma trận 7x24 (7 ngày, từ 8h sáng đến 23h đêm cho gọn)
    heatmap_matrix = [[0]*16 for _ in range(7)] # Cột 0 là 8h, Cột 15 là 23h
    max_val = 0
    
    for item in heatmap_data:
        # Convert Django WeekDay (1=Sun..7=Sat) -> Python (0=Mon..6=Sun)
        # Django: 2(Mon)..7(Sat), 1(Sun)
        wd_django = item['weekday']
        if wd_django == 1:
            wd_idx = 6 # Sun
        else:
            wd_idx = wd_django - 2 # Mon(2)->0, Tue(3)->1...
            
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

# ... (Các hàm manage cũ giữ nguyên)
@user_passes_test(is_staff_user)
def manage_movies(request):
    form = MovieForm()
    movies = Movie.objects.all().order_by('-release_date')
    return render(request, 'cinema_app/manage/manage_movies.html', {'movies': movies, 'form': form})
@user_passes_test(is_staff_user)
def manage_movie_create(request):
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
    movie = get_object_or_404(Movie, pk=pk)
    movie.delete()
    messages.info(request, 'Đã xóa phim.')
    return redirect('manage_movies')
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

# --- QUẢN LÝ NGƯỜI DÙNG (MỚI) ---
@user_passes_test(is_staff_user)
def manage_users(request):
    form = ManageUserForm()
    # Lấy danh sách user kèm profile
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'cinema_app/manage/manage_users.html', {'users': users, 'form': form})

@user_passes_test(is_staff_user)
def manage_user_create(request):
    if request.method == 'POST':
        form = ManageUserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Tạo User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password']
                    )
                    user.is_active = form.cleaned_data['is_active']
                    # Nếu role là STAFF thì set is_staff=True
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
    
    # Nếu lỗi, quay lại trang danh sách (bạn có thể tách trang riêng nếu muốn)
    return redirect('manage_users')

@user_passes_test(is_staff_user)
def manage_user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user) # Auto fix nếu thiếu profile

    if request.method == 'POST':
        form = ManageUserForm(request.POST, instance=user, profile_instance=profile)
        if form.is_valid():
            # 1. Update User
            u = form.save(commit=False)
            new_pass = form.cleaned_data.get('password')
            if new_pass:
                u.set_password(new_pass)
            
            # Đồng bộ is_staff
            role = form.cleaned_data['role']
            if role == 'STAFF':
                u.is_staff = True
            else:
                u.is_staff = False
            u.save()

            # 2. Update Profile
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
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, 'Không thể xóa Superuser (Admin tối cao).')
    elif user == request.user:
        messages.error(request, 'Bạn không thể tự xóa chính mình.')
    else:
        user.delete()
        messages.success(request, 'Đã xóa người dùng.')
    return redirect('manage_users')
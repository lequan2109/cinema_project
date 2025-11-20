# Đường dẫn: cinema_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction, IntegrityError
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date, datetime
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
import json
import uuid
from . import vnpay_helpers

from .models import Movie, CinemaRoom, ShowTime, Ticket, Promotion, Profile
from .forms import (
    RegisterForm, LoginForm, MovieForm, RoomForm, ShowTimeForm, PromotionForm, BookingForm
)

# --- Helpers ---
def is_staff_user(user):
    if not user.is_authenticated:
        return False
    try:
        return user.profile.role == 'STAFF' or user.is_staff
    except Profile.DoesNotExist:
        return user.is_staff

# --- Views Người Dùng ---

def home(request):
    today = timezone.localdate()
    now_showing_movies = Movie.objects.filter(
        release_date__lte=today,
        showtime__start_time__gte=timezone.now()
    ).distinct().order_by('-release_date')
    coming_soon_movies = Movie.objects.filter(
        release_date__gt=today
    ).order_by('release_date')
    upcoming_showtimes = ShowTime.objects.filter(
        start_time__gte=timezone.now()
    ).select_related('movie', 'room').order_by('start_time')[:12]
    return render(request, 'cinema_app/home.html', {
        'now_showing_movies': now_showing_movies,
        'coming_soon_movies': coming_soon_movies,
        'upcoming_showtimes': upcoming_showtimes,
    })

def movie_list(request):
    q = request.GET.get('q', '')
    today = timezone.localdate()
    now_showing_movies = Movie.objects.filter(
        release_date__lte=today,
        title__icontains=q
    ).distinct().order_by('-release_date')
    coming_soon_movies = Movie.objects.filter(
        release_date__gt=today,
        title__icontains=q
    ).order_by('release_date')
    return render(request, 'cinema_app/movie_list.html', {
        'now_showing_movies': now_showing_movies,
        'coming_soon_movies': coming_soon_movies,
        'q': q
    })

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes = ShowTime.objects.filter(
        movie=movie, 
        start_time__gte=timezone.now()
    ).select_related('room').order_by('start_time')
    return render(request, 'cinema_app/movie_detail.html', {
        'movie': movie,
        'showtimes': showtimes,
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
            with transaction.atomic():
                tickets_to_pay = Ticket.objects.filter(booking_code=booking_code, is_paid=False)
                if not tickets_to_pay.exists():
                    messages.warning(request, "Vé này đã được xử lý trước đó.")
                    return redirect('my_tickets')
                
                tickets_to_pay.update(is_paid=True)
                
                # (Logic gửi email sẽ ở đây)
                
                messages.success(request, f"Thanh toán thành công! Vé của bạn đã được xác nhận.")
                return redirect('my_tickets')
                
        except Exception as e:
            messages.error(request, f"Lỗi nghiêm trọng khi cập nhật vé: {str(e)}")
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
            booking_key = f"legacy_{ticket.id}" # Xử lý vé cũ (nếu có)
        
        bookings[booking_key].append(ticket)
        
    processed_bookings = []
    for key, tickets_in_group in bookings.items():
        first_ticket = tickets_in_group[0]
        total_price = sum(t.price_paid for t in tickets_in_group)
        seat_labels = [t.seat_label() for t in tickets_in_group]
        
        processed_bookings.append({
            'booking_code': first_ticket.booking_code, # *** GỬI BOOKING CODE ***
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


# *** THÊM VIEW MỚI ĐỂ THANH TOÁN LẠI ***
@login_required
def retry_payment_view(request, booking_code):
    # 1. Tìm các vé đang chờ của user này
    tickets = Ticket.objects.filter(
        user=request.user,
        booking_code=booking_code,
        is_paid=False
    )
    
    if not tickets.exists():
        messages.error(request, "Không tìm thấy đơn hàng chờ thanh toán này.")
        return redirect('my_tickets')

    # 2. Kiểm tra xem suất chiếu còn hợp lệ không
    first_ticket = tickets.first()
    if first_ticket.showtime.start_time < timezone.now():
        messages.error(request, "Đã quá giờ chiếu. Không thể thanh toán.")
        # Xóa vé chờ
        tickets.delete()
        return redirect('my_tickets')

    # 3. Tính tổng số tiền
    total_price = sum(t.price_paid for t in tickets)
    
    # 4. Tạo URL VNPAY mới (dùng lại booking_code cũ)
    payment_url = vnpay_helpers.get_vnpay_payment_url(
        request=request,
        booking_code=booking_code,
        total_price=total_price
    )
    
    return redirect(payment_url)
# *** KẾT THÚC VIEW MỚI ***


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
        # Sửa: Chỉ đếm vé và doanh thu đã thanh toán
        'tickets': Ticket.objects.filter(is_paid=True).count(),
        'revenue': Ticket.objects.filter(is_paid=True).aggregate(total=Sum('price_paid'))['total'] or 0,
    }
    return render(request, 'cinema_app/manage/dashboard.html', {'stats': stats})

# (Các hàm manage_movies, manage_rooms, manage_showtimes, manage_promotions, manage_reports giữ nguyên)
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
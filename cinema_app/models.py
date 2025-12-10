# Đường dẫn: cinema_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

class Profile(models.Model):
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('STAFF', 'Staff'),
    )
    # Thêm hạng thành viên
    MEMBERSHIP_CHOICES = (
        ('SILVER', 'Bạc'),
        ('GOLD', 'Vàng'),
        ('DIAMOND', 'Kim Cương'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    
    # *** MỚI: Tích điểm & Hạng ***
    points = models.PositiveIntegerField(default=0)
    membership_level = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='SILVER')

    def __str__(self):
        return self.user.username

    # Hàm cập nhật hạng dựa trên điểm
    def update_membership(self):
        if self.points >= 5000: # Ví dụ: 10.000 điểm = Kim Cương
            self.membership_level = 'DIAMOND'
        elif self.points >= 1000: # 4.000 điểm = Vàng
            self.membership_level = 'GOLD'
        else:
            self.membership_level = 'SILVER'
        self.save()

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text='Thời lượng (phút)')
    genre = models.CharField(max_length=100)
    release_date = models.DateField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    trailer_url = models.TextField( blank=True, null=True)
    age_limit = models.PositiveIntegerField(default=0, help_text="Giới hạn độ tuổi xem phim")

    def __str__(self):
        return self.title

# *** MỚI: Model Đánh Giá Phim ***
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # Một người chỉ đánh giá 1 phim 1 lần
        unique_together = ('movie', 'user') 

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}*)"

class CinemaRoom(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField(default=8, validators=[MinValueValidator(1)])
    cols = models.PositiveIntegerField(default=12, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.name} ({self.rows}x{self.cols})"

    @property
    def total_seats(self):
        return self.rows * self.cols

class ShowTime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    room = models.ForeignKey(CinemaRoom, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.movie.title} - {self.room.name} - {self.start_time}"

    @property
    def end_time(self):
        try:
            return self.start_time + timedelta(minutes=self.movie.duration)
        except:
            return self.start_time

class Promotion(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='tickets')
    booking_code = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    seat_row = models.CharField(max_length=2)
    seat_number = models.PositiveIntegerField()
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False) 
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('showtime', 'seat_row', 'seat_number')
        ordering = ['-booked_at']

    def seat_label(self):
        return f"{self.seat_row}{self.seat_number}"

    def __str__(self):
        return f"{self.user.username} - {self.showtime} - {self.seat_label()}"

# *** MỚI: Model Đồ Ăn ***
class Food(models.Model):
    CATEGORY_CHOICES = (
        ('POPCORN', 'Bỏng ngô'),
        ('DRINK', 'Nước uống'),
        ('CANDY', 'Kẹo'),
        ('SNACK', 'Đồ ăn vặt'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='foods/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

# *** MỚI: Model Chi tiết Đơn đặt đồ ăn ***
class FoodOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_orders')
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='food_orders')
    order_code = models.CharField(max_length=100, db_index=True, unique=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-ordered_at']

    def __str__(self):
        return f"{self.user.username} - {self.order_code}"

# *** MỚI: Model Sản phẩm trong đơn đặt đồ ăn ***
class FoodOrderItem(models.Model):
    food_order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.food.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
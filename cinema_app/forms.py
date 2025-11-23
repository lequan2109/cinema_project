# Đường dẫn: cinema_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# --- QUAN TRỌNG: Thêm Profile vào dòng import này ---
from .models import Movie, CinemaRoom, ShowTime, Promotion, Ticket, Review, Profile 

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    full_name = forms.CharField(max_length=255, required=False, label="Họ tên")

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "password1", "password2")

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, label="Tài khoản")
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'duration', 'genre', 'release_date', 'poster', 'age_limit', 'trailer_url']

    def clean_trailer_url(self):
        trailer_url = self.cleaned_data.get('trailer_url')
        if trailer_url and not "<iframe" in trailer_url:
            raise forms.ValidationError("URL trailer phải là mã nhúng (iframe).")
        return trailer_url

class RoomForm(forms.ModelForm):
    class Meta:
        model = CinemaRoom
        fields = ['name', 'rows', 'cols']

class ShowTimeForm(forms.ModelForm):
    class Meta:
        model = ShowTime
        fields = ['movie', 'room', 'start_time', 'base_price']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['code', 'discount_percent', 'valid_until', 'is_active']
        widgets = {
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }

class BookingForm(forms.Form):
    seats = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'placeholder': 'Nhập các ghế...'}))
    promo_code = forms.CharField(max_length=20, required=False)

    def clean_seats(self):
        seats = self.cleaned_data.get('seats')
        if not seats: return []
        seats_list = seats.split(",")
        return [seat.strip() for seat in seats_list]

# --- Form Đánh Giá ---
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Chia sẻ cảm nhận của bạn về phim...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'})
        }

# --- Form Quản Lý Người Dùng ---
class ManageUserForm(forms.ModelForm):
    username = forms.CharField(label="Tài khoản")
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu", required=False, help_text="Để trống nếu không đổi")
    is_active = forms.BooleanField(label="Kích hoạt", required=False, initial=True)
    
    # Các field của Profile
    full_name = forms.CharField(label="Họ tên", max_length=255, required=False)
    phone = forms.CharField(label="Số điện thoại", max_length=20, required=False)
    role = forms.ChoiceField(label="Vai trò", choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_active']

    def __init__(self, *args, **kwargs):
        self.profile_instance = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)
        if self.profile_instance:
            self.fields['full_name'].initial = self.profile_instance.full_name
            self.fields['phone'].initial = self.profile_instance.phone
            self.fields['role'].initial = self.profile_instance.role
        
        if self.instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Movie, CinemaRoom, ShowTime, Promotion

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "full_name", "password1", "password2")

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

from django import forms
from .models import Movie

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'duration', 'genre', 'release_date', 'poster', 'age_limit','trailer_url']  # Bỏ trailer_url

    # Kiểm tra mã iframe YouTube hợp lệ
    def clean_trailer_url(self):
        trailer_url = self.cleaned_data.get('trailer_url')
        if trailer_url and not "<iframe" in trailer_url:
            raise forms.ValidationError("URL trailer phải là mã nhúng (iframe).")
        return trailer_url


class RoomForm(forms.ModelForm):
    class Meta:
        model = CinemaRoom
    # corrected
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

from django import forms
from .models import Ticket, ShowTime

class BookingForm(forms.Form):
    seats = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'placeholder': 'Nhập các ghế, ví dụ: A10, A11'}))  # Nhiều ghế
    promo_code = forms.CharField(max_length=20, required=False)

    def clean_seats(self):
        seats = self.cleaned_data.get('seats')
        seats_list = seats.split(",")  # Chia tách các ghế
        return [seat.strip() for seat in seats_list]

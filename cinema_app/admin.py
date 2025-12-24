from django.contrib import admin

from .models import CinemaRoom, Movie, Profile, Promotion, Review, ShowTime, Ticket


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'membership_level', 'points')
    list_filter = ('role', 'membership_level')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'duration', 'genre')
    list_filter = ('release_date', 'genre')
    search_fields = ('title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('movie__title', 'user__username')


@admin.register(CinemaRoom)
class CinemaRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'rows', 'cols', 'total_seats')


@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'room', 'start_time', 'base_price')
    list_filter = ('start_time',)
    search_fields = ('movie__title',)


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_until', 'is_active')
    list_filter = ('is_active', 'valid_until')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'showtime', 'seat_label', 'price_paid', 'is_paid', 'booked_at')
    list_filter = ('is_paid', 'booked_at')
    search_fields = ('user__username', 'booking_code')

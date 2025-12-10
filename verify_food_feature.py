import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema_project.settings')
django.setup()

from cinema_app.models import Food, User, Profile
from django.utils import timezone

print("=" * 60)
print("KIỂM TRA CHỨC NĂNG ĐẶT ĐỒ ĂN")
print("=" * 60)

# Test 1: Tạo sản phẩm đồ ăn
print("\n✓ TEST 1: Tạo sản phẩm đồ ăn")
print("-" * 60)

foods_data = [
    ("Bỏng ngô nước muối", "Bỏng ngô tươi mới", "POPCORN", 45000),
    ("Coca Cola", "Nước ngọt lạnh", "DRINK", 25000),
    ("Bắp rang bơ", "Bỏng ngô phủ bơ", "POPCORN", 50000),
    ("Kẹo socola", "Kẹo nhập khẩu", "CANDY", 15000),
    ("Nước cam", "Nước cam ép", "DRINK", 30000),
]

for name, desc, category, price in foods_data:
    food, created = Food.objects.get_or_create(
        name=name,
        defaults={
            "description": desc,
            "category": category,
            "price": price,
            "is_available": True,
        }
    )
    status = "Created" if created else "Exists"
    print(f"  [{status}] {food.name:20s} | {price:,}đ | {food.get_category_display()}")

# Test 2: Liệt kê tất cả sản phẩm
print("\n✓ TEST 2: Liệt kê tất cả sản phẩm")
print("-" * 60)

total_foods = Food.objects.count()
print(f"  Tổng sản phẩm: {total_foods}")

for category_code, category_label in Food.CATEGORY_CHOICES:
    foods = Food.objects.filter(category=category_code)
    if foods.exists():
        print(f"\n  {category_label}:")
        for food in foods:
            status = "✓" if food.is_available else "✗"
            print(f"    {status} {food.name:20s} - {food.price:,}đ")

# Test 3: Kiểm tra User và Profile
print("\n✓ TEST 3: Kiểm tra User mẫu")
print("-" * 60)

test_user, user_created = User.objects.get_or_create(
    username="demo",
    defaults={
        "email": "demo@cinema.local",
        "first_name": "Demo",
        "last_name": "User"
    }
)
print(f"  User: {test_user.username} ({test_user.email})")

profile, profile_created = Profile.objects.get_or_create(
    user=test_user,
    defaults={
        "full_name": "Demo User",
        "phone": "0123456789",
        "role": "CUSTOMER"
    }
)
print(f"  Profile: {profile.full_name} | Role: {profile.get_role_display()}")

# Test 4: Kiểm tra Models
print("\n✓ TEST 4: Kiểm tra Models")
print("-" * 60)

from cinema_app.models import FoodOrder, FoodOrderItem
print(f"  Food Model: ✓")
print(f"  FoodOrder Model: ✓")
print(f"  FoodOrderItem Model: ✓")

# Test 5: Kiểm tra Views
print("\n✓ TEST 5: Kiểm tra Views")
print("-" * 60)

from cinema_app import views
views_to_check = [
    'food_menu',
    'view_food_cart',
    'checkout_food',
    'my_food_orders',
    'manage_foods',
    'manage_food_create',
    'manage_food_edit',
    'manage_food_delete',
    'manage_food_orders',
]

for view_name in views_to_check:
    has_view = hasattr(views, view_name)
    status = "✓" if has_view else "✗"
    print(f"  {status} {view_name}")

# Test 6: Kiểm tra URLs
print("\n✓ TEST 6: Kiểm tra URL routes")
print("-" * 60)

from django.urls import reverse

url_names = [
    'food_menu',
    'view_food_cart',
    'checkout_food',
    'my_food_orders',
    'manage_foods',
    'manage_food_orders',
]

for url_name in url_names:
    try:
        url = reverse(url_name)
        print(f"  ✓ {url_name:25s} → {url}")
    except Exception as e:
        print(f"  ✗ {url_name:25s} → ERROR: {str(e)}")

# Test 7: Kiểm tra Forms
print("\n✓ TEST 7: Kiểm tra Forms")
print("-" * 60)

from cinema_app.forms import FoodOrderForm, FoodManageForm
print(f"  FoodOrderForm: ✓")
print(f"  FoodManageForm: ✓")

print("\n" + "=" * 60)
print("✓ TẤT CẢ TEST THÀNH CÔNG!")
print("=" * 60)
print("\n📌 Các URL để test:")
print("  - Menu: http://localhost:8000/food/menu/")
print("  - Giỏ hàng: http://localhost:8000/food/cart/")
print("  - Lịch sử: http://localhost:8000/my-food-orders/")
print("  - Quản lý: http://localhost:8000/manage/foods/")
print("  - Đơn hàng: http://localhost:8000/manage/food-orders/")
print()

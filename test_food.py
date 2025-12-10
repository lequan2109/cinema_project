"""
Test Script để kiểm tra chức năng đặt đồ ăn
Chạy: python manage.py shell < test_food.py
"""

from cinema_app.models import Food, FoodOrder, FoodOrderItem, User, Profile
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# === TEST 1: Tạo các sản phẩm đồ ăn ===
print("=" * 50)
print("TEST 1: Tạo sản phẩm đồ ăn")
print("=" * 50)

foods_data = [
    {
        "name": "Bỏng ngô nước muối",
        "description": "Bỏng ngô tươi mới, vừa nướng",
        "category": "POPCORN",
        "price": 45000,
    },
    {
        "name": "Coca Cola",
        "description": "Nước ngọt lạnh",
        "category": "DRINK",
        "price": 25000,
    },
    {
        "name": "Bắp rang bơ",
        "description": "Bỏng ngô phủ bơ thơm",
        "category": "POPCORN",
        "price": 50000,
    },
    {
        "name": "Kẹo socola",
        "description": "Kẹo socola nhập khẩu",
        "category": "CANDY",
        "price": 15000,
    },
    {
        "name": "Nước cam tươi",
        "description": "Nước cam ép tươi",
        "category": "DRINK",
        "price": 30000,
    },
]

created_foods = []
for food_data in foods_data:
    food, created = Food.objects.get_or_create(
        name=food_data["name"],
        defaults={
            "description": food_data["description"],
            "category": food_data["category"],
            "price": food_data["price"],
            "is_available": True,
        }
    )
    created_foods.append(food)
    status = "✓ Created" if created else "✓ Already exists"
    print(f"{status}: {food.name} - {food.price}đ")

print(f"\nTổng sản phẩm: {len(created_foods)}")

# === TEST 2: Liệt kê tất cả sản phẩm ===
print("\n" + "=" * 50)
print("TEST 2: Liệt kê tất cả sản phẩm")
print("=" * 50)

all_foods = Food.objects.all()
for food in all_foods:
    print(f"- {food.name} ({food.get_category_display()}) - {food.price}đ - Available: {food.is_available}")

# === TEST 3: Lọc theo danh mục ===
print("\n" + "=" * 50)
print("TEST 3: Lọc sản phẩm theo danh mục")
print("=" * 50)

for category_code, category_label in Food.CATEGORY_CHOICES:
    foods = Food.objects.filter(category=category_code)
    print(f"\n{category_label}:")
    if foods.exists():
        for food in foods:
            print(f"  - {food.name} ({food.price}đ)")
    else:
        print("  (Không có sản phẩm)")

# === TEST 4: Tạo đơn hàng test ===
print("\n" + "=" * 50)
print("TEST 4: Tạo đơn hàng test")
print("=" * 50)

# Lấy hoặc tạo user test
test_user, user_created = User.objects.get_or_create(
    username="testuser",
    defaults={
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
)
print(f"Test User: {test_user.username} ({test_user.email})")

# Tạo hoặc get profile
profile, profile_created = Profile.objects.get_or_create(
    user=test_user,
    defaults={
        "full_name": "Test User",
        "phone": "0123456789"
    }
)

# Tạo đơn hàng
order_code = f"FOOD-TEST-{int(timezone.now().timestamp())}"
food_order = FoodOrder.objects.create(
    user=test_user,
    order_code=order_code,
    total_price=0,
    is_paid=False
)
print(f"✓ Created FoodOrder: {food_order.order_code}")

# Thêm items vào đơn hàng
total = 0
for i, food in enumerate(created_foods[:3]):  # Thêm 3 sản phẩm
    quantity = i + 1
    item = FoodOrderItem.objects.create(
        food_order=food_order,
        food=food,
        quantity=quantity,
        unit_price=food.price,
        subtotal=food.price * quantity
    )
    total += item.subtotal
    print(f"  - Added: {food.name} x{quantity} = {item.subtotal}đ")

# Cập nhật total
food_order.total_price = total
food_order.save()
print(f"\n✓ Order Total: {food_order.total_price}đ")

# === TEST 5: Hiển thị thông tin đơn hàng ===
print("\n" + "=" * 50)
print("TEST 5: Hiển thị thông tin đơn hàng")
print("=" * 50)

order = FoodOrder.objects.get(order_code=order_code)
print(f"Order Code: {order.order_code}")
print(f"Customer: {order.user.profile.full_name}")
print(f"Order Time: {order.ordered_at}")
print(f"Status: {'Paid' if order.is_paid else 'Pending'}")
print(f"Items:")
for item in order.items.all():
    print(f"  - {item.food.name} x{item.quantity} = {item.subtotal}đ")
print(f"Total: {order.total_price}đ")

print("\n" + "=" * 50)
print("✓ Tất cả test thành công!")
print("=" * 50)

# HƯỚNG DẪN NHANH - CHỨC NĂNG ĐẶT ĐỒ ĂN

## 🎯 TỔNG QUAN

Chức năng đặt đồ ăn đã được thêm thành công vào hệ thống rạp chiếu phim. Khách hàng có thể xem menu, đặt đồ ăn, và thanh toán. Nhân viên có thể quản lý sản phẩm đồ ăn và xem đơn hàng.

---

## 🔧 BƯỚC CHUẨN BỊ

### 1. Tạo dữ liệu ban đầu (Seeding)

Thêm một số sản phẩm đồ ăn vào database:

```python
from cinema_app.models import Food

# Thêm các sản phẩm đồ ăn
foods = [
    Food.objects.create(
        name="Bỏng ngô nước muối",
        description="Bỏng ngô tươi mới, vừa nướng",
        category="POPCORN",
        price=45000,
        is_available=True
    ),
    Food.objects.create(
        name="Coca Cola",
        description="Nước ngọt lạnh",
        category="DRINK",
        price=25000,
        is_available=True
    ),
    Food.objects.create(
        name="Bắp rang bơ",
        description="Bỏng ngô phủ bơ thơm",
        category="POPCORN",
        price=50000,
        is_available=True
    ),
    Food.objects.create(
        name="Kẹo socola",
        description="Kẹo socola nhập khẩu",
        category="CANDY",
        price=15000,
        is_available=True
    ),
]
```

Hoặc chạy từ Django Shell:
```bash
python manage.py shell
```

---

## 👥 CÁC NHÂN VẬT

### Khách Hàng
- **Menu Đồ Ăn**: `http://localhost:8000/food/menu/`
- **Giỏ Hàng**: `http://localhost:8000/food/cart/`
- **Lịch Sử**: `http://localhost:8000/my-food-orders/`

### Nhân Viên (Staff)
- **Quản Lý Đồ Ăn**: `http://localhost:8000/manage/foods/`
- **Quản Lý Đơn Hàng**: `http://localhost:8000/manage/food-orders/`

---

## 📱 QUY TRÌNH KHÁCH HÀNG

### Bước 1: Xem Menu
```
Vào: /food/menu/
↓
- Chọn danh mục (Bỏng ngô, Nước uống, Kẹo, Đồ ăn vặt)
- Xem hình ảnh & giá
- Chọn số lượng
- Bấm "Thêm vào giỏ"
```

### Bước 2: Xem Giỏ Hàng
```
Vào: /food/cart/
↓
- Hiển thị danh sách sản phẩm đã chọn
- Có thể thay đổi số lượng
- Có thể xóa sản phẩm
- Hiển thị tổng tiền
```

### Bước 3: Thanh Toán
```
Bấm "Tiếp tục thanh toán"
↓
Vào: /food/checkout/
↓
- Xác nhận thông tin khách hàng
- Xác nhận danh sách sản phẩm
- Bấm "Thanh toán" → Chuyển sang VNPAY
```

### Bước 4: Xem Lịch Sử
```
Vào: /my-food-orders/
↓
- Xem tất cả đơn hàng đã đặt
- Xem trạng thái thanh toán
- Xem chi tiết sản phẩm trong từng đơn
```

---

## 👨‍💼 QUY TRÌNH NHÂN VIÊN

### Quản Lý Sản Phẩm

#### Thêm Sản Phẩm Mới
```
Vào: /manage/foods/
↓
Bấm nút "+" (Thêm mới)
↓
Điền form:
- Tên sản phẩm
- Mô tả
- Danh mục
- Giá
- Hình ảnh
- Trạng thái
↓
Bấm "Thêm Mới"
```

#### Sửa Sản Phẩm
```
Vào: /manage/foods/
↓
Bấm nút "✏️" (Sửa)
↓
Cập nhật thông tin
↓
Bấm "Cập nhật"
```

#### Xóa Sản Phẩm
```
Vào: /manage/foods/
↓
Bấm nút "🗑️" (Xóa)
↓
Confirm xóa
```

### Quản Lý Đơn Hàng

```
Vào: /manage/food-orders/
↓
- Xem danh sách tất cả đơn hàng
- Hiển thị: Mã đơn, Khách hàng, Số SP, Tổng tiền, Trạng thái
- Bấm "Chi tiết" để xem thông tin chi tiết
```

---

## 💾 DATABASE SCHEMA

### Food (Đồ Ăn)
| Trường | Kiểu | Ghi chú |
|--------|------|--------|
| id | int | Primary Key |
| name | varchar(255) | Tên sản phẩm |
| description | text | Mô tả |
| category | varchar(20) | POPCORN, DRINK, CANDY, SNACK |
| price | decimal(8,2) | Giá bán |
| image | image | Hình ảnh (upload_to: foods/) |
| is_available | boolean | Có sẵn hay không |
| created_at | datetime | Ngày tạo |

### FoodOrder (Đơn Đặt)
| Trường | Kiểu | Ghi chú |
|--------|------|--------|
| id | int | Primary Key |
| user_id | int | FK → User |
| showtime_id | int | FK → ShowTime (optional) |
| order_code | varchar(100) | Mã đơn (unique) |
| total_price | decimal(10,2) | Tổng tiền |
| is_paid | boolean | Đã thanh toán |
| ordered_at | datetime | Thời gian đặt |

### FoodOrderItem (Chi tiết đơn)
| Trường | Kiểu | Ghi chú |
|--------|------|--------|
| id | int | Primary Key |
| food_order_id | int | FK → FoodOrder |
| food_id | int | FK → Food |
| quantity | int | Số lượng |
| unit_price | decimal(8,2) | Giá lúc đặt |
| subtotal | decimal(10,2) | Tổng (tính tự động) |

---

## 🔐 QUY ỨNG DỤNG

- **@login_required**: Các trang khách hàng yêu cầu đăng nhập
- **@user_passes_test(is_staff_user)**: Các trang quản lý chỉ staff được dùng
- **localStorage**: Giỏ hàng lưu trên client, không mất khi đóng tab
- **Session**: Dữ liệu giỏ cũng được lưu trong server session khi checkout

---

## 🎨 FRONT-END

### localStorage (Client-side)
- Giỏ hàng lưu dưới dạng JSON trong `localStorage['foodCart']`
- Cấu trúc: `{foodId: {name, price, quantity}}`

### Modal
- Thêm sản phẩm dùng modal (không reload trang)
- Chi tiết đơn hàng dùng modal (không mở trang mới)

### UI Framework
- Bootstrap 5 (từ base template)
- Font Awesome icons
- Responsive design (mobile-friendly)

---

## ⚡ TÍNH NĂNG NỔI BẬT

✅ **Giỏ hàng client-side**: Không cần request server liên tục  
✅ **Modal UI**: UX mượt mà, không reload trang  
✅ **Real-time subtotal**: Tính tổng tiền ngay lập tức  
✅ **Đơn hàng truy vết**: Mã đơn duy nhất cho mỗi đơn hàng  
✅ **Quản lý hình ảnh**: Upload hình ảnh cho sản phẩm  
✅ **Filter by category**: Lọc sản phẩm theo danh mục  
✅ **Tích hợp VNPAY**: Thanh toán trực tuyến  

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Food model not found"
```bash
python manage.py migrate
```

### Lỗi: "Module not imported"
- Kiểm tra file `forms.py` đã import Food chưa
- Kiểm tra file `views.py` đã import Food chưa

### Giỏ hàng không hiển thị
- Kiểm tra localStorage trong Dev Tools (F12)
- Clear localStorage: `localStorage.clear()`
- Refresh trang

### Hình ảnh không hiển thị
- Kiểm tra file có trong `media/foods/` chưa
- Kiểm tra settings.py có cấu hình MEDIA_URL & MEDIA_ROOT
- Kiểm tra permission cho thư mục media

---

## 📞 HỖ TRỢ

Nếu có bất kỳ vấn đề nào:
1. Kiểm tra console (F12) để xem lỗi JavaScript
2. Kiểm tra Django logs để xem lỗi server
3. Xem file `FOOD_ORDER_FEATURE.md` để hiểu chi tiết hơn


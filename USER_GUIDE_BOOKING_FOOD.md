# 🎬 QUY TRÌNH ĐẶT VÉ & ĐỒ ĂN - CHI TIẾT TỪNG BƯỚC

## 📌 TỔNG QUAN

Người dùng có 2 luồng chính:
1. **Đặt vé xem phim** (Booking)
2. **Đặt đồ ăn & thức uống** (Food Order)

Có thể làm riêng lẻ hoặc kết hợp cả 2.

---

## 🎫 LUỒNG 1: ĐẶT VÉ XEM PHIM

### Bước 1: Xem Danh Sách Phim
```
URL: http://localhost:8000/
hoặc: http://localhost:8000/movies/

Giao diện:
- Hiển thị phim "Đang chiếu"
- Hiển thị phim "Sắp chiếu"
- Có tìm kiếm & lọc theo thể loại

Thao tác:
👉 Click vào hình poster hoặc tên phim
```

### Bước 2: Xem Chi Tiết Phim
```
URL: http://localhost:8000/movies/{movie_id}/

Giao diện:
- Thông tin phim: tên, mô tả, thời lượng, tuổi
- Poster & trailer
- Danh sách suất chiếu sắp tới

Thao tác:
👉 Chọn suất chiếu muốn xem (ngày/giờ)
👉 Click vào suất chiếu → Chuyển sang Booking
```

### Bước 3: Chọn Ghế & Đặt Vé
```
URL: http://localhost:8000/schedule/{showtime_id}/booking/

PHẢI ĐĂNG NHẬP trước (redirect to login nếu chưa)

Giao diện:
┌─────────────────────┐
│     CHIẾU PHIM      │
│  [Màn hình]         │
│                     │
│  A  [  ][  ][  ]    │  🟩 Ghế trống (xanh)
│  B  [■][■][■]       │  🟥 Ghế đã bán (đỏ)
│  C  [■][  ][■]      │  🟨 Ghế đang giữ (vàng)
│  D  [  ][  ][  ]    │
└─────────────────────┘
         Giá: 50.000đ

Khuyến mãi: [Nhập mã code]

[+ Thêm ghế]  [Xóa]  [Đặt vé]

Thao tác:
1️⃣ Click vào ghế trống
   - Ghế được tô xanh (selected)
   - Hệ thống tự khóa ghế trong 10 phút

2️⃣ Có thể click nhiều ghế
   - Hiển thị số ghế & tổng tiền

3️⃣ (Optional) Nhập mã khuyến mãi
   - Hệ thống kiểm tra & tính giảm giá

4️⃣ Click "Đặt vé"
   - Tạo Ticket record (is_paid=False)
   - Khóa ghế trong database
   - Chuyển sang thanh toán
```

### Bước 4: Thanh Toán (VNPAY)
```
URL: http://localhost:8000/booking/payment-return/
(được redirect từ VNPAY sau thanh toán)

Giao diện:
- Xác nhận: Phim, suất chiếu, ghế, tổng tiền
- [THANH TOÁN]

Thao tác:
1️⃣ Click "Thanh toán"
   - Redirect sang VNPAY gateway
   - Người dùng nhập thông tin thẻ/ví

2️⃣ VNPAY xử lý & redirect về cinema site

3️⃣ Nếu thành công:
   ✅ Cập nhật Ticket: is_paid=True
   ✅ Cộng điểm tích lũy
   ✅ Gửi vé điện tử qua email
   ✅ Hiển thị thông báo "Đặt vé thành công!"

4️⃣ Nếu thất bại:
   ❌ Hiển thị lỗi
   ❌ Xóa Ticket tạm thời
   ❌ Nhắc thử lại
```

### Bước 5: Xem Vé
```
URL: http://localhost:8000/my-tickets/

Giao diện:
- Danh sách các đơn vé đã đặt
- Nhóm theo booking_code
- Hiển thị:
  📅 Phim: Avengers
  🕐 Suất chiếu: 19:00 - Phòng 1
  🪑 Ghế: A1, A2, A3
  💰 Tổng tiền: 150.000đ
  ✅ Trạng thái: Đã thanh toán

Thao tác:
👉 Click vào vé để xem chi tiết
👉 Có nút "In vé" (để in qua lễ tân)
👉 Nếu chưa thanh toán: nút "Thanh toán lại"
👉 Nếu chưa thanh toán: nút "Hủy đơn"
```

---

## 🍿 LUỒNG 2: ĐẶT ĐỒ ĂN & THỨC UỐNG

### Bước 1: Vào Menu Đồ Ăn
```
URL: http://localhost:8000/food/menu/

PHẢI ĐĂNG NHẬP (redirect nếu chưa)

Giao diện:
┌────────────────────────────────────┐
│   MENU ĐỒ ĂN & THỨC UỐNG          │
├────────────────────────────────────┤
│ [Tất cả] [Bỏng ngô] [Nước] [Kẹo] │
└────────────────────────────────────┘

[Bỏng ngô nước muối]  [Coca Cola]  [Kẹo socola]
   45.000đ             25.000đ      15.000đ
   Bỏng ngô tươi mới   Nước lạnh    Kẹo nhập khẩu
   
   -[0]+  [Thêm vào giỏ]
   
                          ┌─────────────┐
                          │ GIỎ CỦA BẠN │
                          ├─────────────┤
                          │ Coca Cola   │
                          │ 1 x 25.000đ │
                          │ [Xóa]       │
                          │             │
                          │ Tổng: 25.000│
                          │ [Xem giỏ]   │
                          └─────────────┘

Thao tác:
1️⃣ Chọn danh mục (bỏng ngô, nước, kẹo, etc)
   - Danh sách cập nhật

2️⃣ Chọn số lượng
   - Dùng nút +/- hoặc nhập trực tiếp

3️⃣ Click "Thêm vào giỏ"
   - Sản phẩm được lưu vào localStorage
   - Sidebar giỏ cập nhật
   - Thông báo "Đã thêm vào giỏ"

4️⃣ Lặp lại cho sản phẩm khác
   - Có thể thêm nhiều sản phẩm

5️⃣ Click "Xem giỏ hàng"
   - Chuyển sang trang giỏ chi tiết
```

### Bước 2: Xem & Chỉnh Sửa Giỏ Hàng
```
URL: http://localhost:8000/food/cart/

Giao diện:
┌─────────────────────────────────────┐
│  GIỎ HÀNG ĐỒ ĂN                    │
├─────────────────────────────────────┤
│ Sản phẩm    │ Số lượng │ Giá │ Tổng │
├─────────────────────────────────────┤
│ Coca Cola   │ -[1]+   │ 25k │ 25k  │ [Xóa]
│ Kẹo socola  │ -[2]+   │ 15k │ 30k  │ [Xóa]
├─────────────────────────────────────┤
│                          Tổng: 55.000đ
│
│ [← Quay lại menu] [Tiếp tục thanh toán]
└─────────────────────────────────────┘

Thao tác:
1️⃣ Thay đổi số lượng
   - Click nút +/- hoặc nhập trực tiếp
   - Tổng tiền tự update

2️⃣ Xóa sản phẩm
   - Click nút [Xóa]
   - Sản phẩm bị xóa khỏi giỏ

3️⃣ Quay lại menu
   - Click "[← Quay lại menu]"
   - Tiếp tục thêm sản phẩm

4️⃣ Thanh toán
   - Click "[Tiếp tục thanh toán]"
   - Chuyển sang trang xác nhận
```

### Bước 3: Xác Nhận Đơn Hàng
```
URL: http://localhost:8000/food/checkout/

Giao diện:
┌────────────────────────────────────┐
│   XÁC NHẬN ĐƠN HÀ HÀNG ĐỒ ĂN      │
├────────────────────────────────────┤
│ Thông tin khách:                   │
│ • Tên: Nguyễn Văn A                │
│ • Email: user@email.com            │
│ • SĐT: 0123456789                  │
├────────────────────────────────────┤
│ Chi tiết đơn:                      │
│ Coca Cola        x1    25.000đ     │
│ Kẹo socola       x2    30.000đ     │
├────────────────────────────────────┤
│ Tổng cộng:                 55.000đ │
│
│ [Quay lại]  [Thanh toán VNPAY]
└────────────────────────────────────┘

Thao tác:
1️⃣ Kiểm tra thông tin khách
   - Tên, email, SĐT có đúng không?

2️⃣ Kiểm tra chi tiết đơn
   - Sản phẩm, số lượng, giá có đúng?

3️⃣ Kiểm tra tổng tiền

4️⃣ Click "[Thanh toán VNPAY]"
   - Giỏ được lưu vào session
   - Tạo FoodOrder + FoodOrderItem records
   - Xóa localStorage
   - Redirect sang VNPAY
```

### Bước 4: Thanh Toán (VNPAY)
```
Tương tự như đặt vé

1️⃣ Redirect sang VNPAY gateway
2️⃣ Nhập thông tin thanh toán
3️⃣ VNPAY xử lý
4️⃣ Redirect về cinema site

Nếu thành công:
✅ Cập nhật FoodOrder: is_paid=True
✅ Hiển thị "Đặt hàng thành công!"
✅ (Optional) Gửi email xác nhận

Nếu thất bại:
❌ Hiển thị lỗi
❌ Xóa FoodOrder & items tạm
❌ Nhắc thử lại
```

### Bước 5: Xem Lịch Sử Đơn Hàng
```
URL: http://localhost:8000/my-food-orders/

Giao diện:
┌────────────────────────────────────┐
│   LỊCH SỬ ĐẶT ĐỒ ĂN              │
├────────────────────────────────────┤
│ Mã đơn: FOOD-123-45678             │
│ Thời gian: 03/12/2025 14:30        │
│ Trạng thái: ✅ Đã thanh toán       │
│                                    │
│ Sản phẩm:                          │
│ • Coca Cola x1 = 25.000đ           │
│ • Kẹo socola x2 = 30.000đ          │
│                                    │
│ Tổng cộng: 55.000đ                │
└────────────────────────────────────┘

Thao tác:
👉 Xem danh sách tất cả đơn hàng
👉 Xem chi tiết từng đơn
👉 Nếu chưa thanh toán: nút "Thanh toán lại"
```

---

## 🎯 KẾT HỢP: ĐẶT VÉ + ĐỒ ĂN CÙNG LÚC

### Quy Trình Thông Thường:
```
1. Xem danh sách phim
   ↓
2. Chọn phim → Xem chi tiết
   ↓
3. Chọn suất chiếu → Booking
   ↓
4. Đặt vé (chọn ghế)
   ↓
5. ⭐ HOẶC VÀO MENU ĐỒ ĂN
   ├─ /food/menu/
   ├─ Chọn đồ ăn
   ├─ Thêm vào giỏ
   └─ Thanh toán đồ ăn
   ↓
6. Thanh toán vé (VNPAY)
   ↓
7. Thanh toán đồ ăn (VNPAY) - nếu có
   ↓
8. Nhận vé & hóa đơn qua email
```

---

## 📊 TÓML LẠI: CÁC THAO TÁC

### 🎫 Đặt Vé:
| Thao tác | Nơi | Kết quả |
|---------|-----|--------|
| Xem phim | Home | Danh sách phim |
| Click phim | Movie List | Chi tiết phim + suất chiếu |
| Chọn suất | Movie Detail | Trang booking |
| Click ghế | Booking | Ghế được chọn (selected) |
| Nhập mã KM | Booking | Kiểm tra & tính giảm giá |
| Đặt vé | Booking | Tạo Ticket, redirect VNPAY |
| Thanh toán | VNPAY | Update is_paid=True |
| Xem vé | My Tickets | Hiển thị vé đã đặt |

### 🍿 Đặt Đồ Ăn:
| Thao tác | Nơi | Kết quả |
|---------|-----|--------|
| Vào menu | Home | Menu đồ ăn |
| Lọc danh mục | Food Menu | Danh sách cập nhật |
| Chọn SL | Food Menu | Update số lượng |
| Thêm giỏ | Food Menu | Lưu localStorage |
| Xem giỏ | Food Cart | Hiển thị chi tiết |
| Sửa SL | Food Cart | Tính toán lại tổng |
| Xóa SP | Food Cart | Xóa khỏi giỏ |
| Checkout | Food Checkout | Tạo FoodOrder |
| Thanh toán | VNPAY | Update is_paid=True |
| Xem lịch sử | My Food Orders | Hiển thị đơn đã đặt |

---

## 🔐 ĐIỀU KIỆN & CẤN PHẢI

### ✅ Luôn cần:
- Phải đăng nhập (@login_required)
- Phải là user thường (không admin)

### ✅ Đặt vé thêm:
- Suất chiếu phải chưa diễn ra
- Ghế phải trống
- Phải có giá base_price

### ✅ Đặt đồ ăn thêm:
- Sản phẩm phải có is_available=True
- Giá phải > 0

### ✅ Thanh toán:
- VNPAY config phải đúng
- Order code phải unique
- Tổng tiền phải > 0

---

## 💾 DỮ LIỆU ĐƯỢC LƯU

### Đặt Vé:
```
✅ Ticket record (is_paid=False)
✅ booking_code (mã đơn)
✅ seat_row, seat_number (ghế)
✅ price_paid (giá thanh toán)
✅ booked_at (thời gian)

Sau thanh toán:
✅ is_paid = True
✅ Cộng điểm (points)
✅ Update membership level
```

### Đặt Đồ Ăn:
```
✅ FoodOrder record (is_paid=False)
   - user
   - order_code
   - total_price
   - ordered_at

✅ FoodOrderItem records (mỗi sản phẩm)
   - food_id
   - quantity
   - unit_price
   - subtotal

Sau thanh toán:
✅ is_paid = True
```

---

## 🚨 CÓ THỂ GẶP VẤN ĐỀ

### Đặt Vé:
- ❌ "Ghế đã được mua" → Ghế bị người khác chọn trước
- ❌ "Đã quá giờ chiếu" → Suất chiếu đã qua
- ❌ "Thanh toán lỗi" → Lỗi kết nối VNPAY

### Đặt Đồ Ăn:
- ❌ "Giỏ trống" → Chưa thêm sản phẩm
- ❌ "Sản phẩm hết hàng" → is_available=False
- ❌ "Thanh toán lỗi" → Lỗi kết nối VNPAY

---

## 📱 MOBILE VS DESKTOP

### Mobile (Điện thoại):
✅ Responsive design
✅ Touch-friendly buttons
✅ Dễ sử dụng
⚠️ May bị lag nếu network chậm

### Desktop (Máy tính):
✅ Giao diện rõ ràng
✅ Sơ đồ ghế lớn
✅ Dễ quản lý

---

## ✨ TIPS & TRICKS

1. **Giỏ hàng sẽ lưu** khi bạn đóng tab
   → Không mất dữ liệu

2. **Ghế được khóa 10 phút**
   → Bạn có time để thanh toán

3. **Có thể giữ vé chưa thanh toán**
   → Nút "Thanh toán lại" để trả góp?

4. **Mã khuyến mãi chỉ áp cho vé**
   → Không áp cho đồ ăn

5. **Đặt vé & đồ ăn riêng rẽ**
   → Có thể thanh toán lần lượt

---

**Bây giờ bạn đã hiểu hoàn toàn quy trình! 🎬🍿**


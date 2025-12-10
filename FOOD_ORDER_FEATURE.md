# HƯỚNG DẪN CHỨC NĂNG ĐẶT ĐỒ ĂN

## 📋 CÁC CHỨC NĂNG ĐÃ THÊM

### 1. **CHO KHÁCH HÀNG**

#### 1.1 Xem Menu Đồ Ăn
- **URL**: `/food/menu/`
- **Mô tả**: Hiển thị danh sách đồ ăn & thức uống có sẵn
- **Tính năng**:
  - Lọc theo danh mục (Bỏng ngô, Nước uống, Kẹo, Đồ ăn vặt)
  - Xem hình ảnh, mô tả, giá
  - Chọn số lượng và thêm vào giỏ
  - Giỏ hàng lưu trong localStorage (không mất khi đóng tab)

#### 1.2 Giỏ Hàng Đồ Ăn
- **URL**: `/food/cart/`
- **Mô tả**: Xem chi tiết giỏ hàng, điều chỉnh số lượng
- **Tính năng**:
  - Cập nhật số lượng từng sản phẩm
  - Xóa sản phẩm khỏi giỏ
  - Hiển thị tổng tiền
  - Nút để tiếp tục thanh toán

#### 1.3 Thanh Toán Đồ Ăn
- **URL**: `/food/checkout/`
- **Mô tả**: Xác nhận đơn hàng trước khi thanh toán
- **Tính năng**:
  - Hiển thị thông tin khách hàng
  - Hiển thị chi tiết từng sản phẩm
  - Tính tổng tiền
  - Redirect sang VNPAY để thanh toán

#### 1.4 Lịch Sử Đơn Đặt Đồ Ăn
- **URL**: `/my-food-orders/`
- **Mô tả**: Xem lịch sử các đơn đặt đồ ăn
- **Tính năng**:
  - Hiển thị tất cả đơn hàng của người dùng
  - Hiển thị trạng thái thanh toán
  - Chi tiết sản phẩm trong từng đơn

---

### 2. **CHO NHÂN VIÊN QUẢN TRỊ**

#### 2.1 Quản Lý Danh Sách Đồ Ăn
- **URL**: `/manage/foods/`
- **Mô tả**: Xem danh sách tất cả đồ ăn
- **Tính năng**:
  - Hiển thị tên, danh mục, giá, trạng thái
  - Nút Sửa (Edit) để cập nhật thông tin
  - Nút Thêm mới (Add) - hiển thị modal
  - Nút Xóa (Delete)

#### 2.2 Thêm Đồ Ăn Mới
- **URL**: `/manage/foods/create/`
- **Mô tả**: Thêm sản phẩm đồ ăn mới vào hệ thống
- **Form Fields**:
  - Tên sản phẩm
  - Mô tả
  - Danh mục (Bỏng ngô, Nước uống, Kẹo, Đồ ăn vặt)
  - Giá
  - Hình ảnh
  - Trạng thái có sẵn (checkbox)

#### 2.3 Sửa Thông Tin Đồ Ăn
- **URL**: `/manage/foods/<id>/edit/`
- **Mô tả**: Cập nhật thông tin sản phẩm

#### 2.4 Xóa Đồ Ăn
- **URL**: `/manage/foods/<id>/delete/`
- **Mô tả**: Xóa sản phẩm khỏi hệ thống

#### 2.5 Quản Lý Đơn Đặt Đồ Ăn
- **URL**: `/manage/food-orders/`
- **Mô tả**: Xem tất cả đơn hàng từ khách hàng
- **Tính năng**:
  - Hiển thị mã đơn, khách hàng, số SP, tổng tiền
  - Hiển thị thời gian đặt
  - Hiển thị trạng thái thanh toán
  - Nút Chi tiết (xem thông tin chi tiết trong modal)

---

## 📊 CÁC MODEL MỚI

### Food (Đồ Ăn)
```python
- id: int (primary key)
- name: string (tên sản phẩm)
- description: text (mô tả)
- category: choice (POPCORN, DRINK, CANDY, SNACK)
- price: decimal (giá bán)
- image: image (hình ảnh)
- is_available: boolean (có sẵn hay không)
- created_at: datetime
```

### FoodOrder (Đơn Đặt Đồ Ăn)
```python
- id: int (primary key)
- user: FK(User) (khách hàng)
- showtime: FK(ShowTime) (suất chiếu - tùy chọn)
- order_code: string (mã đơn hàng duy nhất)
- total_price: decimal (tổng tiền)
- is_paid: boolean (đã thanh toán chưa)
- ordered_at: datetime
```

### FoodOrderItem (Chi Tiết Đơn Hàng)
```python
- id: int (primary key)
- food_order: FK(FoodOrder) (liên kết với đơn hàng)
- food: FK(Food) (liên kết với sản phẩm)
- quantity: int (số lượng)
- unit_price: decimal (giá lúc đặt)
- subtotal: decimal (tổng tiền dòng)
```

---

## 🔗 CÁC API AJAX (Backend)

### `/api/add-to-food-cart/`
- **Method**: POST
- **Dữ liệu**: `{food_id, quantity}`
- **Mục đích**: Thêm sản phẩm vào giỏ (session)

### `/api/remove-food-from-cart/`
- **Method**: POST
- **Dữ liệu**: `{food_id}`
- **Mục đích**: Xóa sản phẩm khỏi giỏ (session)

---

## 📝 CÁC TEMPLATES MỚI

1. **food_menu.html** - Trang menu đồ ăn
2. **food_cart.html** - Trang giỏ hàng
3. **food_checkout.html** - Trang xác nhận đơn hàng
4. **my_food_orders.html** - Trang lịch sử đơn hàng
5. **manage_foods.html** - Trang quản lý danh sách đồ ăn
6. **manage_food_orders.html** - Trang quản lý đơn hàng

---

## 🚀 CÁCH SỬ DỤNG

### Cho Khách Hàng:
1. Đăng nhập vào hệ thống
2. Vào `/food/menu/` để xem menu
3. Chọn sản phẩm, nhập số lượng, click "Thêm vào giỏ"
4. Xem giỏ hàng tại `/food/cart/`
5. Click "Tiếp tục thanh toán" → `/food/checkout/`
6. Confirm đơn hàng → Thanh toán VNPAY
7. Xem lịch sử tại `/my-food-orders/`

### Cho Nhân Viên:
1. Vào `/manage/foods/` để quản lý danh sách
2. Click "Thêm mới" để thêm sản phẩm mới (Modal)
3. Click "Sửa" để cập nhật thông tin
4. Click "Xóa" để xóa sản phẩm
5. Vào `/manage/food-orders/` để xem đơn hàng từ khách
6. Click "Chi tiết" để xem thông tin chi tiết trong modal

---

## ⚙️ CÁC URL ROUTE

**Customer Routes:**
```
GET  /food/menu/                    - Xem menu
GET  /food/cart/                    - Xem giỏ hàng
GET  /food/checkout/                - Trang xác nhận
POST /food/checkout/                - Submit đơn hàng
GET  /my-food-orders/               - Lịch sử đơn hàng

POST /api/add-to-food-cart/         - Thêm vào giỏ (AJAX)
POST /api/remove-food-from-cart/    - Xóa khỏi giỏ (AJAX)
```

**Staff Routes:**
```
GET  /manage/foods/                 - Danh sách đồ ăn
GET  /manage/foods/create/          - Thêm mới
POST /manage/foods/create/          - Submit thêm mới
GET  /manage/foods/<id>/edit/       - Sửa
POST /manage/foods/<id>/edit/       - Submit sửa
GET  /manage/foods/<id>/delete/     - Xóa

GET  /manage/food-orders/           - Danh sách đơn hàng
```

---

## 📦 MIGRATION

Các migration mới đã được tạo:
- `0006_food_foodorder_foodorderitem.py`

Chạy: `python manage.py migrate`

---

## 🎯 TÓM TẮT CHỨC NĂNG

✅ Khách hàng có thể xem, chọn, và đặt đồ ăn  
✅ Giỏ hàng lưu trong localStorage (client-side)  
✅ Tích hợp thanh toán VNPAY  
✅ Nhân viên có thể quản lý sản phẩm đồ ăn  
✅ Nhân viên có thể xem tất cả đơn hàng  
✅ Khách hàng có thể xem lịch sử đơn hàng  


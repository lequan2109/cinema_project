# 🚀 HƯỚNG DẪN SETUP DỰ ÁN (CHO NGƯỜI MỚI)

## 📋 YÊU CẦU

- Python 3.8+
- Git
- pip (đi kèm với Python)

---

## ✅ BƯỚC 1: CLONE DỰ ÁN

```bash
git clone <URL_REPO>
cd cinema_project
```

---

## ✅ BƯỚC 2: TẠO VIRTUAL ENVIRONMENT

### Windows (PowerShell):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Dấu hiệu thành công:** Terminal sẽ hiển thị `(venv)` ở đầu dòng

---

## ✅ BƯỚC 3: CÀI ĐẶT DEPENDENCIES

```bash
pip install -r requirements.txt
```

**Cần kiên nhẫn**, cài đặt sẽ mất **2-5 phút** tùy tốc độ mạng.

---

## ✅ BƯỚC 4: SETUP DATABASE

### 4.1 Tạo Migration (nếu chưa có)
```bash
python manage.py makemigrations
```

### 4.2 Chạy Migration
```bash
python manage.py migrate
```

**Output sẽ như thế này:**
```
Operations to perform:
  Apply all migrations: admin, auth, cinema_app, contenttypes, sessions
Running migrations:
  Applying admin.0001_initial... OK
  Applying auth.0001_initial... OK
  ... (nhiều dòng)
  Applying cinema_app.0006_food_foodorder_foodorderitem... OK
```

---

## ✅ BƯỚC 5: TẠO SUPER USER (ADMIN)

```bash
python manage.py createsuperuser
```

**Sẽ hỏi:**
```
Username: admin
Email address: admin@example.com
Password: 
Password (again): 
```

**Lưu ý:** 
- Username có thể là bất kỳ (vd: `admin`, `root`, tên bạn, etc)
- Password sẽ không hiển thị khi gõ (bình thường)
- Nhập password 2 lần phải trùng nhau

---

## ✅ BƯỚC 6: (OPTIONAL) SEED DỮ LIỆU MẪU

Nếu muốn có dữ liệu mẫu (phim, suất chiếu, đồ ăn) để test:

```bash
python manage.py shell
```

Sau đó trong Python shell:
```python
from cinema_app.seed import seed_data
seed_data()
exit()
```

**Hoặc:** Chạy file seed trực tiếp
```bash
python -c "from cinema_app.seed import seed_data; seed_data()"
```

---

## ✅ BƯỚC 7: CHẠY SERVER

```bash
python manage.py runserver
```

**Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## ✅ BƯỚC 8: TRUY CẬP

### Trang chính:
```
http://localhost:8000/
```

### Admin panel:
```
http://localhost:8000/admin/
```
Đăng nhập bằng super user vừa tạo

---

## 📋 QUY TRÌNH HOÀN CHỈNH (DỄ NHỚ)

```bash
# 1. Clone
git clone <URL>
cd cinema_project

# 2. Virtual env
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# hoặc: source venv/bin/activate  # Linux/Mac

# 3. Install packages
pip install -r requirements.txt

# 4. Database
python manage.py migrate

# 5. Tạo admin
python manage.py createsuperuser

# 6. (Optional) Seed data
python -c "from cinema_app.seed import seed_data; seed_data()"

# 7. Chạy server
python manage.py runserver

# 8. Truy cập: http://localhost:8000/
```

---

## 🔍 KIỂM TRA CÓ LỖI KHÔNG

Trước khi chạy server, kiểm tra:

```bash
python manage.py check
```

**Output bình thường:**
```
System check identified no issues (0 silenced).
```

**Nếu có lỗi:** Sẽ hiển thị chi tiết lỗi, cần fix trước khi chạy.

---

## 🐛 TROUBLESHOOTING

### ❌ Lỗi: "No module named 'django'"
**Giải pháp:** Chưa cài packages
```bash
pip install -r requirements.txt
```

### ❌ Lỗi: "ModuleNotFoundError: No module named 'venv'"
**Giải pháp:** Virtual env chưa activate
```bash
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
```

### ❌ Lỗi: "Error: That port is already in use"
**Giải pháp:** Port 8000 đang bị dùng, chỉ định port khác
```bash
python manage.py runserver 8001
```
Sau đó truy cập: `http://localhost:8001/`

### ❌ Lỗi: "No such table: cinema_app_..."
**Giải pháp:** Chưa run migration
```bash
python manage.py migrate
```

### ❌ Lỗi: "VNPAY not configured"
**Giải pháp:** Cần cấu hình VNPAY trong `settings.py`
- Nếu dev: Không cần, thanh toán test
- Nếu production: Cần merchant code & secret key từ VNPAY

---

## 📦 requirements.txt VÀ CÁC PACKAGE

**File `requirements.txt` chứa:**
- Django (web framework)
- Pillow (xử lý ảnh)
- python-dateutil (xử lý ngày tháng)
- requests (HTTP requests)
- và các package khác

**Khi chạy `pip install -r requirements.txt`:**
- pip tự động tải & cài tất cả packages
- Cả dependencies của dependencies
- Tốn network & thời gian lần đầu

---

## 🔐 SECURITY NOTES (PRODUCTION)

Nếu deploy lên production:

1. **Đổi SECRET_KEY** trong `settings.py`
   ```python
   SECRET_KEY = 'new-secure-key-from-secrets-generator'
   ```

2. **Set DEBUG = False**
   ```python
   DEBUG = False
   ```

3. **Set ALLOWED_HOSTS**
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Tạo `.env` file** để lưu sensitive data
   ```
   SECRET_KEY=...
   DATABASE_URL=...
   VNPAY_MERCHANT_CODE=...
   ```

5. **Dùng production server** (gunicorn, uwsgi)
   ```bash
   gunicorn cinema_project.wsgi:application
   ```

---

## 📊 STRUCTURE SAU KHI SETUP

```
cinema_project/
├── venv/                  ← Virtual environment (sau khi tạo)
├── db.sqlite3            ← Database (sau khi migrate)
├── manage.py
├── requirements.txt
├── cinema_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   ├── static/
│   └── migrations/
├── cinema_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── ...
```

---

## ✨ ĐỢI GÌ THÊM?

Sau khi setup:
- ✅ Truy cập `http://localhost:8000/` → Trang chính
- ✅ Truy cập `http://localhost:8000/admin/` → Admin panel
- ✅ Có thể tạo user mới để test
- ✅ Có thể đặt vé, đặt đồ ăn
- ✅ Có thể xem dữ liệu trong admin

---

## 📞 GẶP PROBLEM?

1. Check lại từng bước (đặc biệt migration & virtualenv)
2. Chạy `python manage.py check` để detect lỗi
3. Check console output (error message thường rất chi tiết)
4. Google error message: "django <error message>"

---

**Chúc bạn setup thành công! 🎉**


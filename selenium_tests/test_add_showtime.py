from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# =========================
# KHỞI TẠO DRIVER
# =========================
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 15)

# =========================
# LOGIN
# =========================
from datetime import datetime, timedelta

def set_datetime_local(driver, element, days_from_now=1, hour=18, minute=30):
    """
    Set giá trị cho input type=datetime-local theo format HTML5
    Ví dụ: 2025-12-02T18:30
    """
    target_time = datetime.now() + timedelta(days=days_from_now)
    value = target_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    datetime_str = value.strftime("%Y-%m-%dT%H:%M")

    driver.execute_script(
        "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));",
        element,
        datetime_str
    )

driver.get("http://127.0.0.1:8000/login/")
time.sleep(2)

# Nhập username
wait.until(EC.presence_of_element_located((By.ID, "id_username"))).send_keys("staff")
time.sleep(1)

# Nhập password
driver.find_element(By.ID, "id_password").send_keys("123")
time.sleep(1)

# Submit
driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

# Chờ login thành công
wait.until(EC.url_contains("/manage"))
print("✅ Đăng nhập thành công")
time.sleep(2)

# =========================
# VÀO TRANG QUẢN LÝ SUẤT CHIẾU
# =========================
driver.get("http://127.0.0.1:8000/manage/showtimes/")
time.sleep(2)

# =========================
# TC_01 – THÊM SUẤT CHIẾU THÀNH CÔNG
# =========================
Select(wait.until(EC.presence_of_element_located((By.ID, "id_movie")))).select_by_visible_text("Avatar: Fire and Ash")
Select(driver.find_element(By.ID, "id_room")).select_by_visible_text("P1 (8x12)")
# Thời gian hợp lệ
start_time = driver.find_element(By.ID, "id_start_time")
set_datetime_local(driver, start_time, days_from_now=1)
time.sleep(1)

# Giá vé
price = driver.find_element(By.ID, "id_base_price")
price.clear()
price.send_keys("75000")
time.sleep(1)

# Submit
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(1)

# Popup xác nhận
alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
alert.accept()

time.sleep(2)
assert "thành công" in driver.page_source.lower()
print("✅ TC_01 PASS")



# =========================
# TC_02 – KHÔNG CHỌN PHIM
# =========================
print("▶️ TC_02 – Không chọn phim")

driver.refresh()
time.sleep(2)

Select(driver.find_element(By.ID, "id_movie")).select_by_index(0)
Select(driver.find_element(By.ID, "id_room")).select_by_index(1)

driver.find_element(By.ID, "id_start_time").send_keys("2025-12-02T18:30")
driver.find_element(By.ID, "id_base_price").send_keys("75000")
time.sleep(1)

driver.find_element(By.XPATH, "//button[@type='submit']").click()

time.sleep(1)
assert "chọn phim" in driver.page_source.lower()
print("✅ TC_02 PASS")

# =========================
# TC_05 – GIÁ VÉ ÂM
# =========================
print("▶️ TC_05 – Giá vé âm")

driver.refresh()
time.sleep(2)

Select(driver.find_element(By.ID, "id_movie")).select_by_index(1)
Select(driver.find_element(By.ID, "id_room")).select_by_index(1)

driver.find_element(By.ID, "id_start_time").send_keys("2025-12-02T18:30")

price = driver.find_element(By.ID, "id_base_price")
price.clear()
price.send_keys("-5")
time.sleep(1)

driver.find_element(By.XPATH, "//button[@type='submit']").click()

time.sleep(1)
assert "giá vé" in driver.page_source.lower()
print("✅ TC_05 PASS")

# =========================
# KẾT THÚC
# =========================
print("🎉 HOÀN THÀNH TẤT CẢ TEST CASE")
time.sleep(3)
driver.quit()

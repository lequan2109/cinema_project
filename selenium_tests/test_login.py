from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

driver.get("http://127.0.0.1:8000/login/")

wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("staff")
driver.find_element(By.NAME, "password").send_keys("123")
driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)

# Kiểm tra login thành công
wait.until(EC.url_contains("/manage"))

print("✅ Login thành công")
driver.quit()

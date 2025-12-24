from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:8000")

input("Nhấn Enter để đóng...")
driver.quit()

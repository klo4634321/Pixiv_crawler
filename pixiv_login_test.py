from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 訪問登入頁面
url = "https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh_tw&source=pc&view_type=page"
driver.get(url)

# 等待登入表單加載
time.sleep(3)

# 輸入用戶名和密碼
elem_user = driver.find_element(By.XPATH, "//input[@placeholder='信箱地址或pixiv ID']")
elem_user.send_keys("123@gmail.com")

elem_pwd = driver.find_element(By.XPATH, "//input[@placeholder='密碼']")
elem_pwd.send_keys("456")
elem_pwd.send_keys(Keys.RETURN)

# 等待登入完成並跳轉到主頁
time.sleep(5)
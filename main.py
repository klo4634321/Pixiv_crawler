import os
import time
import re
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 指定畫師ID
#ARTIST_ID = "48631"

class PixivSimpleSeleniumDownloader:
    def __init__(self, username, password, artist_id, chromedriver_path=None):
        """初始化下載器"""
        self.username = username
        self.password = password
        self.artist_id = artist_id
        self.chromedriver_path = chromedriver_path
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Referer': 'https://www.pixiv.net/',
        }
        
        # 保存目錄
        self.save_dir = f"pixiv_artist_{self.artist_id}"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def login_with_selenium(self):
        """使用Selenium登入Pixiv並獲取cookies"""
        print("正在使用Selenium登入Pixiv...")
        
        try:
            # 初始化WebDriver，使用提供的路徑或自動下載
            if self.chromedriver_path:
                driver = webdriver.Chrome(self.chromedriver_path)
            else:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service)
            
            # 訪問登入頁面
            url = "https://accounts.pixiv.net/login?return_to=https%3A%2F%2Fwww.pixiv.net%2F&lang=zh_tw&source=pc&view_type=page"
            driver.get(url)
            
            # 等待登入表單加載
            time.sleep(3)
            
            # 輸入用戶名和密碼
            elem_user = driver.find_element(By.XPATH, "//input[@placeholder='信箱地址或pixiv ID']")
            elem_user.send_keys(self.username)

            elem_pwd = driver.find_element(By.XPATH, "//input[@placeholder='密碼']")
            elem_pwd.send_keys(self.password)

            elem_pwd.send_keys(Keys.RETURN)
            
            # 等待登入完成並跳轉到主頁
            time.sleep(5)
            
            # 確認登入狀態
            if "pixiv.net/dashboard" in driver.current_url or "pixiv.net/" == driver.current_url:
                print("登入成功！")
            else:
                print("可能登入失敗，請檢查頁面狀態")
            
            # 獲取cookies
            cookies = driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # 訪問畫師頁面，進一步確認登入狀態
            driver.get(f"https://www.pixiv.net/users/{self.artist_id}/artworks")
            time.sleep(3)
            
            # 再次更新cookies
            cookies = driver.get_cookies()
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            print("成功獲取cookies")
            driver.quit()
            return True
            
        except Exception as e:
            print(f"登入過程中發生錯誤: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            return False
    
    def get_artwork_ids(self):
        """獲取畫師的作品ID列表"""
        url = f"https://www.pixiv.net/ajax/user/{self.artist_id}/profile/all"
        response = self.session.get(url, headers=self.headers)
        
        artwork_ids = []
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data['error'] == False:
                    # 獲取所有插畫ID
                    illusts = data['body']['illusts']
                    if illusts:
                        artwork_ids = list(illusts.keys())
                        print(f"成功獲取 {len(artwork_ids)} 個作品ID")
                    else:
                        print("未找到作品")
                else:
                    print(f"獲取作品列表失敗: {data['message']}")
            except Exception as e:
                print(f"解析作品列表出錯: {str(e)}")
        else:
            print(f"請求失敗: {response.status_code}")
            
        return artwork_ids
    
    def get_artwork_details(self, artwork_id):
        """獲取單個作品的詳細信息"""
        url = f"https://www.pixiv.net/ajax/illust/{artwork_id}"
        response = self.session.get(url, headers=self.headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data['error'] == False:
                    return data['body']
            except Exception as e:
                print(f"解析作品詳情出錯: {str(e)}")
        
        return None
    
    def get_artwork_pages(self, artwork_id):
        """獲取作品的所有頁面URL"""
        url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages"
        response = self.session.get(url, headers=self.headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data['error'] == False:
                    return [page['urls']['original'] for page in data['body']]
            except Exception as e:
                print(f"解析作品頁面出錯: {str(e)}")
        
        return []
    
    def download_image(self, url, filename):
        """下載單張圖片"""
        headers = self.headers.copy()
        headers['Referer'] = 'https://www.pixiv.net/'
        
        try:
            response = self.session.get(url, headers=headers, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"成功下載: {filename}")
                return True
            else:
                print(f"下載失敗 ({response.status_code}): {url}")
        except Exception as e:
            print(f"下載出錯: {str(e)}")
        
        return False
    
    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        return re.sub(r'[\\/*?:"<>|]', '', filename)
    
    def download_artwork(self, artwork_id):
        """下載完整作品（包括多頁）"""
        # 獲取作品詳情
        details = self.get_artwork_details(artwork_id)
        if not details:
            print(f"無法獲取作品 {artwork_id} 的詳細信息")
            return
        
        # 獲取標題並清理非法字符
        title = self.sanitize_filename(details['title'])
        
        # 獲取所有頁面URL
        page_urls = self.get_artwork_pages(artwork_id)
        if not page_urls:
            print(f"無法獲取作品 {artwork_id} 的頁面")
            return
        
        # 下載每一頁
        for i, url in enumerate(page_urls):
            # 提取文件擴展名
            ext = os.path.splitext(urlparse(url).path)[1]
            if not ext:
                ext = '.jpg'
            
            if len(page_urls) > 1:
                filename = os.path.join(self.save_dir, f"{artwork_id}_{title}_{i+1}{ext}")
            else:
                filename = os.path.join(self.save_dir, f"{artwork_id}_{title}{ext}")
            
            # 檢查文件是否已存在
            if os.path.exists(filename):
                print(f"跳過已存在文件: {filename}")
                continue
            
            # 下載圖片
            success = self.download_image(url, filename)
            
            # 添加間隔
            if success and i < len(page_urls) - 1:
                time.sleep(1)
    
    def run(self, max_artworks=5):
        """執行下載程序"""
        # 使用Selenium登入
        if not self.login_with_selenium():
            print("無法使用Selenium登入Pixiv，退出程序")
            return
        
        print(f"準備下載畫師 {self.artist_id} 的作品，最多下載 {max_artworks} 個")
        
        # 獲取作品ID列表
        artwork_ids = self.get_artwork_ids()
        if not artwork_ids:
            print("未獲取到任何作品ID，退出")
            return
        
        # 限制下載數量
        artwork_ids = artwork_ids[:max_artworks]
        print(f"將下載 {len(artwork_ids)} 個作品")
        
        # 下載每個作品
        for i, artwork_id in enumerate(artwork_ids):
            print(f"\n[{i+1}/{len(artwork_ids)}] 下載作品 {artwork_id}")
            self.download_artwork(artwork_id)
            
            # 在下載不同作品之間添加間隔
            if i < len(artwork_ids) - 1:
                time.sleep(2)
        
        print(f"\n下載完成！作品保存在目錄: {self.save_dir}")


if __name__ == "__main__":
    # 輸入Pixiv賬號和密碼
    username = input("請輸入Pixiv帳號 (郵箱或用戶名): ")
    password = input("請輸入Pixiv密碼: ")
    artist_id = input("請輸入畫師ID (https://www.pixiv.net/users/畫師ID/artworks): ")
    # 如果有特定的chromedriver路徑，可以在這裡提供
    chromedriver_path = input("請輸入ChromeDriver路徑 (如果沒有請直接按Enter，將自動下載): ")
    if not chromedriver_path:
        chromedriver_path = None
    
    # 創建下載器並執行

    downloader = PixivSimpleSeleniumDownloader(username, password, artist_id,chromedriver_path)

    # 設置要下載的最大作品數量
    max_artworks = input("請輸入要下載的最大作品數量 (默認5): ")
    max_artworks = int(max_artworks) if max_artworks.isdigit() else 5
    
    # 開始下載
    downloader.run(max_artworks)
# 🎨 Pixiv 圖片下載器 (使用 Selenium)

這是一個簡單的 Python 工具，用來從 Pixiv 自動化登入並下載指定畫師的所有公開作品。  
它會模擬登入、抓取畫師頁面、獲取原始圖像網址，並將圖片下載到本地資料夾中。

<img src="https://img.shields.io/badge/Python-3.10-blue.svg?logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Selenium-%23009639.svg?logo=selenium&logoColor=white" alt="Selenium">
<img src="https://img.shields.io/badge/Webdriver_Manager-%23FFBB00.svg?logo=google-chrome&logoColor=white" alt="WebDriver Manager">
<img src="https://img.shields.io/badge/Pixiv_Crawler-%232F88F6.svg?logo=pixiv&logoColor=white" alt="Pixiv Crawler">

---

## 📦 功能特色

- ✅ 使用 Selenium 自動登入 Pixiv
- ✅ 獲取畫師所有公開作品的原始圖片
- ✅ 支援多頁作品（例如漫畫）
- ✅ 自動跳過已下載圖片
- ✅ 清理檔名中的非法字元

---

## 🧰 使用到的套件

| 套件名稱 | 功能說明 |
|----------|----------|
| `requests` | 處理 API 請求與圖片下載 |
| `selenium` | 自動控制瀏覽器登入並取得 cookies |
| `webdriver-manager` | 自動安裝對應的 ChromeDriver |
| `re` | 清理檔名中的非法字元 |
| `os`, `time`, `urllib.parse` | 檔案與網路路徑處理 |

安裝所有依賴：
```bash
pip install -r requirements.txt
```

## 🚀 使用方法

```bash
python main.py
```


p.s.
pixiv_login_test.py 是測試使用Selenium登入 pixiv

資料來源:
https://home.gamer.com.tw/creationDetail.php?sn=4817720
https://home.gamer.com.tw/creationDetail.php?sn=4861878

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import os

# Set up Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

# Instagram post URL
url = 'https://www.instagram.com/p/Ccr8QyxqCib/'

# Set up Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(20)

try:
    driver.get(url)
except Exception as e:
    print("Error loading page:", e)
    driver.quit()
    exit()

time.sleep(5)  # Let JavaScript finish rendering

# Parse page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extract caption and hashtags
caption_block = soup.find('meta', attrs={"property": "og:description"})
if caption_block:
    caption = caption_block.get("content", "")
    print("Caption:", caption)

    # Get hashtags
    hashtags = [word for word in caption.split() if word.startswith("#")]
    print("Hashtags:", hashtags)

# ✅ Extract image URL
image_block = soup.find('meta', attrs={"property": "og:image"})
if image_block:
    image_url = image_block.get("content", "")
    print("Image URL:", image_url)

    # Download the image
    try:
        img_data = requests.get(image_url).content
        with open("instagram_image.jpg", "wb") as handler:
            handler.write(img_data)
        print("✅ Image downloaded as 'instagram_image.jpg'")
    except Exception as e:
        print("❌ Failed to download image:", e)

driver.quit()

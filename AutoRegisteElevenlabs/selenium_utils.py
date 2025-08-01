import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import WebDriver as SeleniumWebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, WebDriverException
import os

def human_typing(element, text, delay_range=(0.05, 0.15)):
    """
    Gõ từng ký tự vào một trường input với độ trễ ngẫu nhiên để mô phỏng hành vi của con người.
    """
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

def initialize_undetected_chromedriver(proxy_address=None, proxy_username=None, proxy_password=None) -> SeleniumWebDriver:
    """
    Khởi tạo một phiên bản undetected_chromedriver với các tùy chọn cấu hình.
    Tùy chọn hỗ trợ cấu hình proxy có xác thực.
    """
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    
    # === THÊM DÒNG NÀY ===
    options.add_argument("--disable-gpu") # Tắt tăng tốc phần cứng để tránh lỗi màn hình trắng.
    
    options.add_argument("--start-maximized") # Mở trình duyệt toàn màn hình

    # Cấu hình proxy nếu được cung cấp
    if proxy_address:
        print(f"Đang cấu hình trình duyệt với proxy: {proxy_address}")
        if proxy_username and proxy_password:
            # Đây là cú pháp cho proxy có xác thực.
            # undetected_chromedriver thường hỗ trợ SOCKS5 với cú pháp này.
            # Đối với HTTP/S có xác thực, đôi khi cần thêm extension hoặc selenium-wire.
            options.add_argument(f'--proxy-server=http://{proxy_username}:{proxy_password}@{proxy_address}')
            # Nếu proxy là SOCKS5, bạn có thể thử:
            # options.add_argument(f'--proxy-server=socks5://{proxy_username}:{proxy_password}@{proxy_address}')
        else:
            options.add_argument(f'--proxy-server={proxy_address}')
    
    driver = uc.Chrome(options=options)
    return driver

def safe_click(driver: SeleniumWebDriver, by: By, value: str, timeout: int = 10, retry_attempts: int = 3, delay_between_retries: float = 1.0):
    """
    Click vào một phần tử một cách an toàn, xử lý các trường hợp bị chặn hoặc chưa sẵn sàng.
    Sử dụng WebDriverWait, thử click bằng JavaScript nếu click trực tiếp bị chặn, và retry.
    """
    for attempt in range(retry_attempts):
        try:
            # Chờ phần tử có thể click được
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
            
            # Thử click trực tiếp
            element.click()
            print(f"Đã click phần tử {value} (lần thử {attempt + 1}).")
            return True
        except ElementClickInterceptedException:
            print(f"Click trực tiếp phần tử {value} bị chặn. Đang thử click bằng JavaScript (lần thử {attempt + 1})...")
            driver.execute_script("arguments[0].click();", element)
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"Không thể click phần tử {value} (lần thử {attempt + 1}): {type(e).__name__} - {e}")
            if attempt < retry_attempts - 1:
                time.sleep(delay_between_retries) # Đợi trước khi thử lại
            else:
                raise # Ném lỗi nếu đã hết số lần thử
    return False # Không bao giờ đến đây nếu lỗi được ném ở trên

def safe_type(driver: SeleniumWebDriver, by: By, value: str, text: str, timeout: int = 10, retry_attempts: int = 3, delay_between_retries: float = 1.0):
    """
    Gõ văn bản vào một trường input một cách an toàn, xử lý các trường hợp chưa sẵn sàng và retry.
    Sử dụng WebDriverWait và human_typing.
    """
    for attempt in range(retry_attempts):
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
            element.clear() # Xóa nội dung cũ trước khi gõ
            human_typing(element, text)
            print(f"Đã điền văn bản vào phần tử {value} (lần thử {attempt + 1}).")
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"Không thể điền văn bản vào phần tử {value} (lần thử {attempt + 1}): {type(e).__name__} - {e}")
            if attempt < retry_attempts - 1:
                time.sleep(delay_between_retries)
            else:
                raise
    return False

def take_screenshot(driver: SeleniumWebDriver, filename: str = "error_screenshot.png"):
    """
    Chụp ảnh màn hình của trình duyệt và lưu lại.
    """
    screenshot_dir = "screenshots"
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    
    filepath = os.path.join(screenshot_dir, filename)
    try:
        driver.save_screenshot(filepath)
        print(f"Đã chụp ảnh màn hình: {filepath}")
    except Exception as e:
        print(f"Lỗi khi chụp ảnh màn hình: {e}")


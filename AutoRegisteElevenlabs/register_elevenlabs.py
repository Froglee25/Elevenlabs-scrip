import asyncio
import time
import sys
import random
import csv # Import thư viện csv để lưu thông tin tài khoản
import logging # Import thư viện logging
import os # Import os để tạo thư mục
import datetime # Import thư viện datetime

# Import Selenium Exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select 
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, WebDriverException, NoSuchElementException, ElementNotInteractableException

# Import các hàm từ file temp_mail_handler.py
from temp_mail_handler import get_temp_email_address, wait_for_and_get_verification_link, delete_temp_email_api

# Import các hàm tiện ích Selenium từ file selenium_utils.py
from selenium_utils import human_typing, initialize_undetected_chromedriver, safe_click, safe_type, take_screenshot

# Import các hằng số từ config.py
import config

# Cập nhật: Import hàm từ file onboarding_handler.py
from onboarding_handler import handle_onboarding_and_get_api_key

# Cập nhật: Import hàm lưu trữ từ file mới
from file_utils import save_account_result

# Đảm bảo các thư mục cần thiết tồn tại
os.makedirs(config.LOG_DIR, exist_ok=True)
os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
os.makedirs(config.DATA_DIR, exist_ok=True) 

# Cấu hình logging cơ bản
logging.basicConfig(
    level=config.LOGGING_LEVEL, # Sử dụng cấp độ logging từ config
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOG_DIR, config.LOG_FILE), encoding='utf-8'), # Ghi log vào file
        logging.StreamHandler(sys.stdout) # In log ra console
    ]
)
logger = logging.getLogger(__name__)


# ==============================================================================
# HÀM "WORKFLOW" CHÍNH ĐƯỢC TÁI CẤU TRÚC
# ==============================================================================
async def run_full_registration_workflow():
    """
    Thực hiện toàn bộ quy trình từ đăng ký đến lấy API key cho một tài khoản.
    Quản lý một driver duy nhất cho toàn bộ quá trình.
    Trả về True nếu thành công, False nếu thất bại.
    """
    temp_email_info = {}
    temp_email = ""
    selenium_driver = None

    try:
        # === Giai đoạn 1: Đăng ký và Lấy link ===
        logger.info("Bắt đầu quy trình mới...")
        temp_email_info = await get_temp_email_address()
        if not temp_email_info or not temp_email_info.get('email'):
            logger.error("Không thể lấy email tạm thời. Dừng quy trình.")
            save_account_result(status="Failed - Temp Email API") # Hàm lưu mới
            return False
        
        temp_email = temp_email_info['email']

        logger.info(f"Đang xử lý tài khoản với email: {temp_email}")
        selenium_driver = initialize_undetected_chromedriver()

        selenium_driver.get(config.URLS["sign_up"]) # Sử dụng URL từ config
        time.sleep(config.PAGE_LOAD_DELAY)

        # === THÊM BƯỚC NÀY ===
        # Click vào body để "đánh thức" trang và đảm bảo nội dung được render
        logger.info("Mô phỏng click chuột để lấy focus cho trình duyệt...")
        safe_click(selenium_driver, By.TAG_NAME, 'body', timeout=5)
        # =======================

        # Điền form đăng ký...
        if not safe_type(selenium_driver, By.XPATH, config.SELECTORS["signup_email_input"], temp_email):
            raise Exception("Failed - Email Input")
        if not safe_type(selenium_driver, By.XPATH, config.SELECTORS["signup_password_input"], config.DEFAULT_PASSWORD):
            raise Exception("Failed - Password Input")
        if not safe_click(selenium_driver, By.XPATH, config.SELECTORS["signup_terms_checkbox"]):
            raise Exception("Failed - Terms Checkbox")
        if not safe_click(selenium_driver, By.XPATH, config.SELECTORS["signup_submit_button"]):
            raise Exception("Failed - Signup Button")

        # Đôi khi cần nhấn "Resend" để email được gửi đi ngay lập tức
        logger.info("Đang tìm và click nút 'Resend verification email' (nếu có)...")
        safe_click(selenium_driver, By.XPATH, config.SELECTORS["resend_email_button"], timeout=15)

        logger.info("Đăng ký thành công. Đang chờ link xác minh...")
        
        verification_link = await wait_for_and_get_verification_link(temp_email_info)
        if not verification_link:
            raise Exception("Failed - No Verification Link")

        logger.info(f"Đã có link xác minh. Đang mở link...")
        
        # === Giai đoạn 2: Xác minh, Onboarding và Lấy Key ===
        selenium_driver.get(verification_link)
        time.sleep(config.PAGE_LOAD_DELAY)

        # Xử lý pop-up "Continue" sau khi xác minh email
        logger.info("Đang tìm và click nút 'Continue' trên trang xác minh (nếu có)...")
        try:
            if safe_click(selenium_driver, By.XPATH, config.SELECTORS["continue_button"], timeout=15):
                logger.info("Đã click nút 'Continue' thành công.")
                time.sleep(3) # Đợi trang tải lại sau khi click
            else:
                logger.warning("Không tìm thấy nút 'Continue', có thể trang đã tự động chuyển hướng.")
        except Exception as e:
            logger.warning(f"Lỗi khi tìm nút 'Continue': {e}. Tiếp tục quy trình...")

        # Chờ chuyển hướng đến trang đăng nhập hoặc dashboard
        try:
            WebDriverWait(selenium_driver, config.DEFAULT_WAIT_TIMEOUT).until(
                EC.url_contains("sign-in")
            )
            logger.info("Đã chuyển hướng đến trang đăng nhập.")
        except TimeoutException:
            logger.warning("Không tự động chuyển đến trang đăng nhập, có thể đã đăng nhập sẵn. Tiếp tục...")

        # === BƯỚC BẮT BUỘC: Đăng nhập lại vào tài khoản sau khi xác minh ===
        logger.info("Thực hiện đăng nhập vào tài khoản...")
        
        # Điền email
        if not safe_type(selenium_driver, By.XPATH, config.SELECTORS["signin_email_input"], temp_email):
            raise Exception("Failed - Signin Email Input")
        
        # Điền mật khẩu
        if not safe_type(selenium_driver, By.XPATH, config.SELECTORS["signin_password_input"], config.DEFAULT_PASSWORD):
            raise Exception("Failed - Signin Password Input")
            
        # Click nút Sign in
        if not safe_click(selenium_driver, By.XPATH, config.SELECTORS["signin_submit_button"]):
            raise Exception("Failed - Signin Submit Button")
            
        # Chờ đợi để xác nhận đăng nhập thành công và đã chuyển sang trang onboarding
        try:
            logger.info("Đăng nhập thành công, đang chờ chuyển hướng đến trang onboarding...")
            WebDriverWait(selenium_driver, config.DEFAULT_WAIT_TIMEOUT).until(
                EC.url_contains("/onboarding")
            )
            logger.info("Đã chuyển hướng đến trang onboarding thành công!")
            time.sleep(config.PAGE_LOAD_DELAY)
        except TimeoutException:
            logger.error(f"Đăng nhập thất bại hoặc không chuyển hướng đến trang onboarding. URL hiện tại: {selenium_driver.current_url}")
            raise Exception("Failed - Onboarding Redirect Timeout")
        # ==========================================


        # Gọi hàm xử lý onboarding và lấy key (đã chuyển sang onboarding_handler.py)
        success = await handle_onboarding_and_get_api_key(selenium_driver, temp_email, config.DEFAULT_PASSWORD)
        
        if success:
            logger.info(f"✅ HOÀN TẤT: Đã lấy API Key thành công cho {temp_email}.")
            return True
        else:
            raise Exception("Failed - Onboarding or API Key Extraction")

    except Exception as e:
        error_status = str(e)
        logger.error(f"❌ LỖI trong quy trình của {temp_email}: {error_status}")
        if selenium_driver:
            take_screenshot(selenium_driver, f"error_{temp_email}_{error_status}.png")
        # Lưu thông tin lỗi
        save_account_result(email=temp_email, password=config.DEFAULT_PASSWORD, status=f"Failed - {error_status}")
        return False
    finally:
        if selenium_driver:
            selenium_driver.quit()
        # Xóa email tạm thời sau khi hoàn tất hoặc gặp lỗi
        if temp_email_info and temp_email_info.get('mail_id'):
            await delete_temp_email_api(temp_email_info['mail_id'])

# ==============================================================================
# HÀM CHÍNH MỚI
# ==============================================================================
async def worker(worker_id, semaphore, results_list):
    """
    Hàm worker được quản lý bởi semaphore để chạy quy trình chính.
    """
    async with semaphore:
        logger.info(f"[Worker {worker_id}] Bắt đầu làm việc...")
        success = await run_full_registration_workflow()
        results_list.append(success)
        logger.info(f"[Worker {worker_id}] Đã hoàn thành.")
        # Thêm một khoảng nghỉ ngẫu nhiên nhỏ giữa các worker
        await asyncio.sleep(random.uniform(1, 3))


async def main():
    """
    Hàm chính để điều khiển quá trình đăng ký nhiều tài khoản SONG SONG.
    """
    try:
        num_accounts_to_create = int(input("Bạn muốn tạo bao nhiêu tài khoản ElevenLabs? "))
    except ValueError:
        logger.error("Vui lòng nhập một số hợp lệ.")
        return

    # Semaphore sẽ giới hạn số lượng worker chạy cùng lúc
    semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_WORKERS)
    
    logger.info(f"\nBắt đầu tạo {num_accounts_to_create} tài khoản với tối đa {config.MAX_CONCURRENT_WORKERS} luồng song song...")
    
    tasks = []
    results = []
    for i in range(num_accounts_to_create):
        # Tạo một task cho mỗi worker
        task = asyncio.create_task(worker(i + 1, semaphore, results))
        tasks.append(task)
    
    # Chờ tất cả các task hoàn thành
    await asyncio.gather(*tasks)
    
    success_count = sum(1 for res in results if res is True)
    
    logger.info("\n--- QUÁ TRÌNH HOÀN TẤT ---")
    logger.info(f"Tổng kết: {success_count}/{num_accounts_to_create} tài khoản được tạo thành công.")
    logger.info(f"Kiểm tra file '{os.path.basename(config.ACCOUNTS_WITH_API_KEY_FILE)}' và '{os.path.basename(config.FAILED_REGISTER_ACCOUNTS_FILE)}' để xem kết quả.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\nĐã dừng chương trình.")

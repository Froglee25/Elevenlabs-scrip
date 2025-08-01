import time
import random
import datetime
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select 
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

import config
from selenium_utils import safe_click, safe_type, take_screenshot
from file_utils import save_account_result # Cập nhật: Import từ file mới

logger = logging.getLogger(__name__)

# ==============================================================================
# HÀM HỖ TRỢ ONBOARDING
# ==============================================================================
def generate_random_name():
    """
    Tạo tên ngẫu nhiên từ danh sách có sẵn.
    """
    return random.choice(config.FIRST_NAMES)

def generate_random_dob():
    """
    Tạo ngày sinh ngẫu nhiên, đảm bảo người dùng trên 18 tuổi.
    """
    # Năm sinh ngẫu nhiên từ 18-60 tuổi
    min_year = datetime.datetime.now().year - 60
    max_year = datetime.datetime.now().year - 18
    year = str(random.randint(min_year, max_year))
    # Tháng và ngày ngẫu nhiên
    month = str(random.randint(1, 12))
    day = str(random.randint(1, 28)) # Giảm thiểu lỗi ngày tháng không hợp lệ
    return day, month, year

# THAY THẾ TOÀN BỘ HÀM CŨ BẰNG PHIÊN BẢN NÀY

async def skip_to_api_key_extraction(driver, email, password):
    """
    Xử lý quy trình tạo API key đầy đủ, bao gồm cả pop-up xác nhận quyền.
    """
    try:
        # 1. Điều hướng đến trang API keys
        logger.info("Đang điều hướng đến trang API keys...")
        driver.get(config.URLS["api_keys"])
        time.sleep(config.PAGE_LOAD_DELAY)

        # 2. Click nút "Create API Key"
        logger.info("Đang tìm và click nút 'Create API Key'...")
        if not safe_click(driver, By.XPATH, config.SELECTORS["create_api_key_button"], timeout=20):
            raise Exception("Không tìm thấy nút 'Create API Key'")
        
        # 3. Chờ tên ngẫu nhiên được điền
        logger.info("Pop-up đặt tên đã xuất hiện, đang chờ tên ngẫu nhiên...")
        time.sleep(3)

        # 4. Click nút "Create" trong pop-up
        logger.info("Đang click nút 'Create' để xác nhận tên...")
        if not safe_click(driver, By.XPATH, config.SELECTORS["api_key_final_create_button"], timeout=15):
            raise Exception("Không tìm thấy nút 'Create' cuối cùng trong pop-up")

        # 5. XỬ LÝ BƯỚC MỚI: Click nút "Create Key" trên pop-up cảnh báo "No Permissions"
        logger.info("Đang xử lý pop-up 'No Permissions Selected'...")
        if not safe_click(driver, By.XPATH, config.SELECTORS["confirm_create_key_button"], timeout=15):
            raise Exception("Không tìm thấy nút 'Create Key' trên pop-up cảnh báo")

        # 6. Chờ pop-up cuối cùng hiển thị và lấy giá trị key
        logger.info("Đã xác nhận, đang chờ pop-up hiển thị key...")
        api_key_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, config.SELECTORS["api_key_field_in_popup"]))
        )
        api_key = api_key_input.get_attribute("value")
        
        if not api_key:
            raise Exception("Tìm thấy trường API key, nhưng giá trị rỗng")

        logger.info(f"✅ HOÀN TẤT! Đã lấy API Key thành công: {api_key[:4]}...{api_key[-4:]}")
        save_account_result(email=email, password=password, api_key=api_key)

        # 7. Đóng pop-up cuối cùng
        logger.info("Đang đóng pop-up chứa API key...")
        safe_click(driver, By.XPATH, config.SELECTORS["close_popup_button"], timeout=10)
        
        return True
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"THẤT BẠI trong quy trình lấy API Key: {error_message}")
        take_screenshot(driver, f"error_get_api_key_{email}.png")
        save_account_result(email=email, password=password, status=f"Failed - Get API Key Step: {error_message}")
        return False

async def handle_onboarding_and_get_api_key(driver, email, password):
    # Tăng thời gian chờ mặc định cho các bước onboarding
    ONBOARDING_TIMEOUT = config.DEFAULT_WAIT_TIMEOUT 
    wait = WebDriverWait(driver, ONBOARDING_TIMEOUT)

    # === Xử lý trang Onboarding (Choose your style) ===
    # SỬA: Cải thiện XPath
    onboarding_continue_button_xpath = config.SELECTORS["continue_button"]
    
    logger.info("Đang kiểm tra và click nút 'Continue' trên trang onboarding (nếu có)...")
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, config.SELECTORS["onboarding_style_title"])))
        logger.info("Đã tìm thấy trang 'Choose your style'. Đang tìm nút 'Continue'...")
        time.sleep(2) 

        if safe_click(driver, By.XPATH, onboarding_continue_button_xpath, timeout=ONBOARDING_TIMEOUT, retry_attempts=config.DEFAULT_RETRY_ATTEMPTS): 
            logger.info("Đã click nút 'Continue' trên trang onboarding.")
            time.sleep(3) 
        else:
            logger.info(f"Cảnh báo: Nút 'Continue' không xuất hiện hoặc không click được. Có thể trang đã tự chuyển hướng. URL hiện tại: {driver.current_url}") 
            take_screenshot(driver, f"warning_onboarding_continue_{email}.png")
    except TimeoutException:
        logger.info(f"Không tìm thấy trang 'Choose your style'. Có thể đã bỏ qua hoặc không xuất hiện. URL hiện tại: {driver.current_url}") 
    except Exception as e: 
        logger.warning(f"Lỗi khi tương tác với nút 'Continue' trên onboarding: {e}. URL hiện tại: {driver.current_url}") 
        take_screenshot(driver, f"error_onboarding_{email}.png")


    # === Xử lý trang Personalization (Help us personalize your experience) ===
    logger.info("Đang kiểm tra và xử lý trang cá nhân hóa (nếu có)...")
    try:
        # Tăng thời gian chờ đợi trang cá nhân hóa tải
        wait.until(EC.presence_of_element_located((By.XPATH, config.SELECTORS["personalization_title"])))
        logger.info("Đã tìm thấy trang cá nhân hóa. Đang điền thông tin...")

        random_name = generate_random_name()
        if not safe_type(driver, By.XPATH, config.SELECTORS["personalization_firstname_input"], random_name, timeout=ONBOARDING_TIMEOUT): 
            logger.error(f"Không thể điền tên ngẫu nhiên: {random_name}. URL hiện tại: {driver.current_url}") 
            # Cập nhật: Sử dụng hàm lưu trữ mới
            save_account_result(email=email, password=password, status="Failed - Personalization Name")
            take_screenshot(driver, f"error_personalization_name_{email}.png")
            return False
        logger.info(f"Đã điền tên ngẫu nhiên: {random_name}")

        day, month_num, year = generate_random_dob()
        
        if not safe_type(driver, By.XPATH, config.SELECTORS["personalization_bday_day_input"], day, timeout=ONBOARDING_TIMEOUT): 
            logger.error(f"Không thể điền ngày sinh: {day}. URL hiện tại: {driver.current_url}") 
            # Cập nhật: Sử dụng hàm lưu trữ mới
            save_account_result(email=email, password=password, status="Failed - Personalization Day")
            take_screenshot(driver, f"error_personalization_day_{email}.png")
            return False
        logger.info(f"Đã điền ngày: {day}")

        try:
            month_element = wait.until(EC.presence_of_element_located((By.XPATH, config.SELECTORS["personalization_bday_month_select"])))
            month_select = Select(month_element)
            month_name = datetime.date(1900, int(month_num), 1).strftime("%B") 
            month_select.select_by_visible_text(month_name) 
            logger.info(f"Đã chọn tháng: {month_name}")
            time.sleep(1) 
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Không thể chọn tháng từ dropdown: {e}. URL hiện tại: {driver.current_url}")
            # Cập nhật: Sử dụng hàm lưu trữ mới
            save_account_result(email=email, password=password, status="Failed - Personalization Month Select")
            take_screenshot(driver, f"error_personalization_month_select_{email}.png")
            return False

        if not safe_type(driver, By.XPATH, config.SELECTORS["personalization_bday_year_input"], year, timeout=ONBOARDING_TIMEOUT): 
            logger.error(f"Không thể điền năm sinh: {year}. URL hiện tại: {driver.current_url}") 
            # Cập nhật: Sử dụng hàm lưu trữ mới
            save_account_result(email=email, password=password, status="Failed - Personalization Year")
            take_screenshot(driver, f"error_personalization_year_{email}.png")
            return False
        logger.info(f"Đã điền năm: {year}")
        
        # SỬA: Cải thiện logic để tìm nút "Next" hoặc "Skip"
        if not safe_click(driver, By.XPATH, config.SELECTORS["personalization_next_button"], timeout=ONBOARDING_TIMEOUT): 
            logger.error(f"Không thể click nút 'Next' trên trang cá nhân hóa. Đang thử nút 'Skip'. URL hiện tại: {driver.current_url}")
            if not safe_click(driver, By.XPATH, config.SELECTORS["skip_button"], timeout=ONBOARDING_TIMEOUT):
                logger.error(f"Không thể click nút 'Skip' trên trang cá nhân hóa. Thất bại. URL hiện tại: {driver.current_url}")
                # Cập nhật: Sử dụng hàm lưu trữ mới
                save_account_result(email=email, password=password, status="Failed - Personalization Next/Skip Button")
                take_screenshot(driver, f"error_personalization_next_or_skip_{email}.png")
                return False
            else:
                logger.info("Đã click nút 'Skip' trên trang cá nhân hóa.")
        else:
            logger.info("Đã click nút 'Next' trên trang cá nhân hóa.")
        time.sleep(3) 
        
    except TimeoutException:
        logger.info(f"Không tìm thấy trang cá nhân hóa. Có thể đã bỏ qua hoặc không xuất hiện. URL hiện tại: {driver.current_url}") 
    except Exception as e:
        logger.error(f"Lỗi khi xử lý trang cá nhân hóa: {e}. URL hiện tại: {driver.current_url}") 
        # Cập nhật: Sử dụng hàm lưu trữ mới
        save_account_result(email=email, password=password, status=f"Failed - Personalization Page: {type(e).__name__}")
        take_screenshot(driver, f"error_personalization_general_{email}.png")
        return False
    
    # === Xử lý các trang onboarding còn lại (How did you hear, Choose your platform, What to do, Do more) ===
    # Tất cả các trang này đều có thể bỏ qua bằng nút 'Skip' hoặc 'Continue'
    
    onboarding_pages_to_handle = [
        {"title_xpath": config.SELECTORS["how_hear_title"], "skip_button_xpath": config.SELECTORS["skip_button"]},
        {"title_xpath": config.SELECTORS["choose_platform_title"], "skip_button_xpath": config.SELECTORS["continue_button"]},
        {"title_xpath": config.SELECTORS["what_to_do_title"], "skip_button_xpath": config.SELECTORS["skip_button"]},
        {"title_xpath": config.SELECTORS["do_more_title"], "skip_button_xpath": config.SELECTORS["skip_button"]}
    ]

    for page in onboarding_pages_to_handle:
        try:
            logger.info(f"Đang kiểm tra và xử lý trang onboarding: '{page['title_xpath']}'...")
            wait.until(EC.presence_of_element_located((By.XPATH, page['title_xpath'])))
            logger.info("Đã tìm thấy trang. Đang click nút...")
            if safe_click(driver, By.XPATH, page['skip_button_xpath'], timeout=ONBOARDING_TIMEOUT):
                logger.info("Đã click nút thành công.")
                time.sleep(3)
            else:
                logger.warning(f"Không thể click nút trên trang '{page['title_xpath']}'. Có thể trang đã tự chuyển hướng.")
                take_screenshot(driver, f"warning_{page['title_xpath']}_skip_{email}.png")
        except TimeoutException:
            logger.info(f"Không tìm thấy trang onboarding '{page['title_xpath']}'. Có thể đã bỏ qua. Tiếp tục.")
        except Exception as e:
            logger.error(f"Lỗi không xác định khi xử lý trang onboarding '{page['title_xpath']}': {e}. URL hiện tại: {driver.current_url}")
            take_screenshot(driver, f"error_{page['title_xpath']}_general_{email}.png")
            return False
    
    # --- Hàm mới để điều hướng và lấy API key (tách ra để tái sử dụng) ---
    return await skip_to_api_key_extraction(driver, email, password)

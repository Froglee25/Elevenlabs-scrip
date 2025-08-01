# FILE: config.py
import os
import logging
#from dotenv import load_dotenv

# Tải các biến từ file .env vào môi trường của chương trình
# Thao tác này cần được thực hiện trước khi truy cập các biến
load_dotenv()

# ==============================================================================
# CREDENTIALS & SENSITIVE DATA (Đọc từ biến môi trường)
# ==============================================================================
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD")
TEMP_MAIL_API_TOKEN = os.getenv("TEMP_MAIL_API_TOKEN")

# Thêm một bước kiểm tra an toàn để đảm bảo các biến đã tồn tại
if not DEFAULT_PASSWORD or not TEMP_MAIL_API_TOKEN:
    # Dừng chương trình nếu không tìm thấy thông tin nhạy cảm
    raise ValueError("LỖI: Không tìm thấy DEFAULT_PASSWORD hoặc TEMP_MAIL_API_TOKEN. Hãy chắc chắn bạn đã tạo file .env và điền đủ thông tin.")

# ==============================================================================
# FILE & DIRECTORY PATHS
# ==============================================================================
# Thư mục để lưu trữ logs và ảnh chụp màn hình
LOG_DIR = "logs"
SCREENSHOT_DIR = "screenshots"
DATA_DIR = "file" # Thư mục để lưu trữ các file dữ liệu khác

# Tên file log chính
LOG_FILE = "script_debug.log"

# File dữ liệu thành công
REGISTERED_ACCOUNTS_FILE = os.path.join(DATA_DIR, "registered_accounts_success.csv") # <-- Đổi tên
ACCOUNTS_WITH_API_KEY_FILE = os.path.join(DATA_DIR, "elevenlabs_api_keys_success.csv") # <-- Đổi tên

# THÊM MỚI: File dữ liệu thất bại
FAILED_REGISTER_ACCOUNTS_FILE = os.path.join(DATA_DIR, "registered_accounts_failed.csv")
FAILED_API_KEY_ACCOUNTS_FILE = os.path.join(DATA_DIR, "elevenlabs_api_keys_failed.csv")


# ==============================================================================
# SELENIUM & SCRIPT SETTINGS
# ==============================================================================
# Số lượng trình duyệt tối đa chạy song song
MAX_CONCURRENT_WORKERS = 1

# Thời gian chờ mặc định cho các element xuất hiện (giây)
DEFAULT_WAIT_TIMEOUT = 20

# Số lần thử lại tối đa cho các hành động an toàn (safe_click, safe_type)
DEFAULT_RETRY_ATTEMPTS = 2

# Khoảng thời gian nghỉ giữa các lần xử lý tài khoản (giây)
MIN_DELAY_BETWEEN_ACCOUNTS = 5
MAX_DELAY_BETWEEN_ACCOUNTS = 7

# Khoảng thời gian nghỉ giữa các lần đăng ký tài khoản (giây)
MIN_DELAY_BETWEEN_REGISTRATIONS = 10
MAX_DELAY_BETWEEN_REGISTRATIONS = 20

# Thời gian chờ tải trang mặc định (giây)
PAGE_LOAD_DELAY = 7


# ==============================================================================
# ONBOARDING DATA
# ==============================================================================
FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi",
    "Ivan", "Judy", "Kevin", "Linda", "Mike", "Nancy", "Oscar", "Peggy"
]

# ==============================================================================
# LOGGING SETTINGS
# ==============================================================================
LOGGING_LEVEL = logging.INFO # Cấp độ logging mặc định (DEBUG, INFO, WARNING, ERROR, CRITICAL)


# ==============================================================================
# XPATH & UI SELECTORS
# ==============================================================================
SELECTORS = {
    # === Sign-up & Sign-in ===
    "signup_email_input": '//input[@type="email"]',
    "signup_password_input": '//input[@type="password"]',
    "signup_terms_checkbox": '//*[@id="app-root"]/div[3]/div/div[2]/div/div/form/div[2]/div[2]/div[2]/div/label/button',
    "signup_submit_button": '//*[@id="app-root"]/div[3]/div/div[2]/div/div/form/div[4]/button',
    "resend_email_button": '//*[@id="app-root"]/div[3]/div/div[2]/div/div/form/div[2]/div/button',
    "signin_email_input": '//*[@id="sign-in-form"]/div[1]/div/input',
    "signin_password_input": '//*[@id="sign-in-form"]/div[2]/div/div/div/input',
    "signin_submit_button": '//*[@id="sign-in-form"]/div[3]/button',

    # === General & Pop-ups ===
    "continue_button": '//button[contains(., "Continue")]',
    "skip_button": '//button[contains(., "Skip")]',

    # === Onboarding Pages ===
    "onboarding_style_title": '//h1[normalize-space()="Choose your style"]',
    "personalization_title": '//h5[normalize-space()="Help us personalize your experience"]',
    "personalization_firstname_input": '//*[@id="firstname"]',
    "personalization_bday_day_input": '//*[@id="bday-day"]',
    "personalization_bday_month_select": '//select[@autocomplete="bday-month"]',
    "personalization_bday_year_input": '//*[@id="bday-year"]',
    "personalization_next_button": '//button[normalize-space()="Next"]',
    "how_hear_title": '//*[@id="app-root"]/div[2]/div/div[3]/div/div[1]/div/h5',
    "choose_platform_title": '//h1[normalize-space()="Choose your platform"]',
    "what_to_do_title": '//h5[normalize-space()="What would you like to do with ElevenLabs?"]',
    "do_more_title": '//*[@id="app-root"]/div[2]/div/div[3]/div/div/div/div[1]/div[1]/h5',

    # === API Key Handling ===
    "create_api_key_button": '//button[contains(., "Create API Key")]', # Nút để bắt đầu tạo key
    "api_key_name_input": '//div[@role="dialog"]//input[@name="name"]',
    "api_key_final_create_button": '//div[@role="dialog"]//button[normalize-space()="Create"]',
    "confirm_create_key_button": '//div[@role="dialog"]//button[normalize-space()="Create Key"]', # Nút trên pop-up "No Permissions"
    "api_key_field_in_popup": '//div[@role="dialog"]//input[@readonly]', # Tìm input ở chế độ CHỈ ĐỌC
    "close_popup_button": '//div[@role="dialog"]//button[contains(., "Close")]' # Nút đóng pop-up sau khi lấy key
}


# ==============================================================================
# URLS
# ==============================================================================
URLS = {
    "base": "https://elevenlabs.io",
    "sign_up": "https://elevenlabs.io/sign-up",
    "api_keys": "https://elevenlabs.io/app/settings/api-keys" # <-- URL MỚI VÀ ĐÚNG
}

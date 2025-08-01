import time
import requests
import re
import json # Để xử lý JSON response
import unicodedata # Để làm sạch chuỗi
import config # <-- THÊM DÒNG NÀY

# API Base URL cho tempmail.id.vn
API_BASE_URL = "https://tempmail.id.vn/api"

# BIẾN NÀY CẦN BẠN CUNG CẤP API TOKEN CỦA MÌNH
# HƯỚNG DẪN: Lấy API Token từ trang cá nhân của bạn trên tempmail.id.vn
# API Token chỉ hiển thị 1 lần duy nhất lúc tạo.
# Đảm bảo token có các quyền: mail:create, mail:read, mail:list, mail:delete
# XÓA BỎ DÒNG NÀY -> API_TOKEN = "5219|jcFuZ3Oha439Pj2A6MYdQf8NZftUXvB35LVUghZyec0bc88f"

# Headers chung cho các API request
HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {config.TEMP_MAIL_API_TOKEN}", # <-- SỬA DÒNG NÀY
    "Content-Type": "application/json"
}

def create_temp_email_api() -> dict:
    """
    Tạo một địa chỉ email tạm thời ngẫu nhiên bằng API của tempmail.id.vn.
    Trả về dictionary chứa email và mail_id.
    """
    print("Đang tạo địa chỉ email tạm thời ngẫu nhiên bằng API tempmail.id.vn...")
    url = f"{API_BASE_URL}/email/create"
    
    # === CẬP NHẬT PAYLOAD TẠI ĐÂY ===
    # Gửi payload với user và domain là None để tạo mail ngẫu nhiên
    payload = {"user": None, "domain": None} 
    
    try:
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status() # Ném lỗi cho HTTP errors (4xx hoặc 5xx)
        full_response_data = response.json() 
        
        if full_response_data.get('success') == True: # Kiểm tra 'success' là True
            # Trích xuất trực tiếp từ khóa 'data'
            nested_data = full_response_data.get('data') 
            
            if isinstance(nested_data, dict):
                email = nested_data.get('email')
                mail_id = nested_data.get('id')

                # DEBUG PRINT: In ra giá trị email và mail_id được trích xuất
                print(f"DEBUG: Extracted email: {email}, mail_id: {mail_id}")
                
                if email and mail_id:
                    print(f"Đã tạo email tạm thời: {email} với ID: {mail_id}")
                    return {"email": email, "mail_id": mail_id}
                else:
                    print(f"Lỗi: Không tìm thấy email hoặc ID trong khóa 'data' của phản hồi thành công. Phản hồi đầy đủ: {full_response_data}")
                    return {}
            else:
                print(f"Lỗi: Khóa 'data' không tồn tại hoặc không phải là dictionary trong phản hồi thành công. Phản hồi đầy đủ: {full_response_data}")
                return {}
        else:
            print(f"Lỗi khi tạo email: {full_response_data.get('message', 'Phản hồi không mong muốn')}. Phản hồi đầy đủ: {full_response_data}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối API khi tạo email: {e}")
        return {}

def get_mail_messages_api(mail_id: str) -> list:
    """
    Lấy danh sách các tin nhắn cho một mail_id cụ thể từ API.
    """
    url = f"{API_BASE_URL}/email/{mail_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # Dựa trên log, danh sách tin nhắn nằm trong data['data']['items']
        if data and data.get('success') == True and data.get('data') and isinstance(data['data'].get('items'), list):
            return data['data']['items'] # Trả về danh sách tin nhắn
        else:
            print(f"Lỗi khi lấy danh sách tin nhắn cho mail_id {mail_id}: Phản hồi không mong muốn hoặc không có 'items' trong 'data'. Phản hồi đầy đủ: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối API khi lấy tin nhắn: {e}")
        return []

def get_message_content_api(message_id: str) -> str:
    """
    Đọc nội dung của một tin nhắn cụ thể từ API.
    """
    url = f"{API_BASE_URL}/message/{message_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        if data and data.get('success') == True and data.get('data') and data['data'].get('body'):
            content = data['data']['body'] # Lấy nội dung từ trường 'body'
            # Loại bỏ các ký tự điều khiển, zero-width spaces và non-breaking spaces
            cleaned_content = unicodedata.normalize('NFKD', content).encode('ascii', 'ignore').decode('utf-8')
            cleaned_content = re.sub(r'[\u200b-\u200f\ufeff\xa0]', '', cleaned_content) # Loại bỏ các ký tự đặc biệt khác
            return cleaned_content
        else:
            print(f"Lỗi khi đọc nội dung tin nhắn {message_id}: {data.get('message', 'Phản hồi không mong muốn')}. Phản hồi đầy đủ: {data}")
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối API khi đọc nội dung tin nhắn: {e}")
        return ""

def delete_temp_email_api(mail_id: str) -> bool:
    """
    Xóa một địa chỉ email tạm thời bằng API của tempmail.id.vn.
    Trả về True nếu xóa thành công, False nếu ngược lại.
    """
    print(f"Đang xóa email tạm thời với ID: {mail_id}...")
    url = f"{API_BASE_URL}/email/{mail_id}"
    try:
        response = requests.delete(url, headers=HEADERS) # Sử dụng phương thức DELETE
        response.raise_for_status()
        data = response.json()
        
        if data and data.get('success') == True:
            print(f"Đã xóa email tạm thời ID: {mail_id} thành công.")
            return True
        else:
            print(f"Lỗi khi xóa email ID: {mail_id}: {data.get('message', 'Phản hồi không mong muốn')}. Phản hồi đầy đủ: {data}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối API khi xóa email: {e}")
        return False

# --- Các hàm được gọi từ register_elevenlabs.py ---
# Đã loại bỏ tham số playwright_page vì không còn được sử dụng
async def get_temp_email_address() -> dict: 
    """
    Tạo một địa chỉ email tạm thời bằng API và trả về email cùng mail_id.
    """
    email_info = create_temp_email_api()
    if email_info:
        return email_info
    return {}

async def wait_for_and_get_verification_link(email_info: dict, timeout_seconds: int = 300) -> str:
    """
    Chờ email xác minh từ ElevenLabs trong hộp thư API và trích xuất link.
    """
    email_address = email_info.get('email')
    mail_id = email_info.get('mail_id')

    if not mail_id:
        print("Không có mail_id để kiểm tra email.")
        return None

    print(f"Đang chờ email xác minh đến hộp thư của {email_address} (qua API) trong tối đa {timeout_seconds} giây...")
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        messages = get_mail_messages_api(mail_id)
        
        if messages:
            for msg in messages:
                # Dựa trên log, thông tin email nằm trực tiếp trong mỗi dictionary trong list 'items'
                # Kiểm tra người gửi và tiêu đề của email
                if re.search(r'ElevenLabs', msg.get('sender_name', ''), re.IGNORECASE) and \
                   re.search(r'(verify|confirm)', msg.get('subject', ''), re.IGNORECASE):
                    
                    print(f"Đã tìm thấy email xác minh từ ElevenLabs (ID: {msg.get('id')})!")
                    message_content = get_message_content_api(msg['id'])
                    
                    if message_content:
                        # === TINH CHỈNH REGEX ĐỂ TRÍCH XUẤT LINK ===
                        # Tìm link có chứa "elevenlabs.io/app/action?mode=verifyEmail"
                        # Regex này mạnh mẽ hơn và ít bị ảnh hưởng bởi các tham số khác trong URL
                        # Hỗ trợ cả dấu nháy đơn và kép cho thuộc tính href
                        # Cải thiện regex để bắt được bất kỳ ký tự nào giữa verifyEmail và dấu nháy đóng
                        match = re.search(r'href=["\'](https?://elevenlabs\.io/app/action\?mode=verifyEmail[^"\']*?)["\']', message_content, re.IGNORECASE)
                        if match:
                            link = match.group(1)
                            print(f"Đã trích xuất link xác minh: {link}")
                            return link
                        else:
                            print("Không tìm thấy link xác minh trong nội dung email. Đang thử lại...")
                    else:
                        print(f"Không thể đọc nội dung tin nhắn {msg.get('id')}. Đang thử lại...")
        
        print("Chưa tìm thấy email xác minh từ ElevenLabs. Đang chờ thêm...")
        time.sleep(10) # Đợi 10 giây trước khi kiểm tra lại

    print("Hết thời gian chờ email xác minh.")
    return None

# Script Tự động Tạo tài khoản ElevenLabs

Đây là một script Python được thiết kế để tự động hóa hoàn toàn quá trình đăng ký tài khoản trên nền tảng ElevenLabs. Mục tiêu chính là vượt qua quy trình đăng ký, xác minh email, và onboarding để lấy API key miễn phí một cách tự động và hiệu quả.

## ✨ Tính năng nổi bật

* **Tự động hóa Toàn diện**: Từ việc tạo email tạm thời, điền form, xác minh email, cho đến khi lấy và lưu API key.
* **Sử dụng Email Tạm thời Chuyên nghiệp**: Tích hợp với API của `mail.tm` để tạo email, đảm bảo độ tin cậy cao hơn.
* **Hỗ trợ Chạy Song song**: Sử dụng `asyncio` để tạo nhiều tài khoản cùng lúc, giúp tăng tốc độ đáng kể.
* **Kiến trúc "Thông minh"**: Tự động nhận diện môi trường để chạy với giao diện đồ họa (Local) hoặc ở chế độ ẩn (Colab/Server).
* **Xử lý lỗi & Ghi log chi tiết**: Tự động chụp ảnh màn hình khi có lỗi và ghi lại toàn bộ quá trình vào file log để dễ dàng gỡ lỗi.
* **Quản lý Cấu hình An toàn**: Toàn bộ thông tin nhạy cảm như mật khẩu, API token được quản lý an toàn qua file `.env`.

## 🛠️ Công nghệ sử dụng

* Python 3.8+
* Selenium & Undetected Chromedriver
* Asyncio
* Requests
* API của Mail.tm

## 📋 Yêu cầu

* Python 3.8 trở lên
* Git

## 🚀 Cài đặt & Thiết lập

1.  **Clone repository về máy:**
    ```bash
    git clone [URL-repository-của-bạn]
    cd [tên-thư-mục-dự-án]
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    # Tạo môi trường ảo
    python -m venv venv

    # Kích hoạt trên Windows
    .\venv\Scripts\activate

    # Kích hoạt trên macOS/Linux
    source venv/bin/activate
    ```

3.  **Tạo file `requirements.txt` (nếu chưa có):**
    ```bash
    pip freeze > requirements.txt
    ```

4.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Cấu hình

1.  Tạo một file tên là `.env` trong thư mục gốc của dự án.
2.  Sao chép nội dung dưới đây vào file `.env` và điền các giá trị của bạn:

    ```ini
    # Mật khẩu bạn muốn sử dụng cho các tài khoản ElevenLabs
    DEFAULT_PASSWORD=YourStrongPasswordHere!123

    # API Token lấy từ tài khoản mail.tm của bạn
    MAIL_TM_TOKEN=your_mail_tm_api_token_here

    # (Tùy chọn) Địa chỉ proxy nếu bạn muốn sử dụng
    PROXY_URL=[http://user:password@proxy.example.com:8080](http://user:password@proxy.example.com:8080)
    ```

## ▶️ Cách chạy

1.  Kích hoạt môi trường ảo của bạn.
2.  Chạy lệnh sau trong terminal:
    ```bash
    python register_elevenlabs.py
    ```
3.  Khi được hỏi, nhập số lượng tài khoản bạn muốn tạo và nhấn Enter.
4.  Theo dõi tiến trình qua log trên console. Kết quả cuối cùng sẽ được lưu trong các file `.csv` bên trong thư mục `file/`.

## ⚠️ Lưu ý Quan trọng

* Script này được tạo ra cho mục đích giáo dục và thử nghiệm.
* Vui lòng tuân thủ điều khoản dịch vụ của ElevenLabs.
* Việc lạm dụng công cụ để tạo tài khoản hàng loạt có thể dẫn đến việc tài khoản hoặc địa chỉ IP của bạn bị chặn. Hãy sử dụng một cách có trách nhiệm.

# FILE: file_utils.py
import os
import csv
import time
import logging
import config

logger = logging.getLogger(__name__)

# ==============================================================================
# HÀM LƯU TRỮ CHUNG
# ==============================================================================
def save_account_result(email="N/A", password="N/A", api_key="N/A", status="Success"):
    """
    Lưu kết quả xử lý tài khoản vào file thành công hoặc thất bại.
    """
    is_success = "Success" in status or api_key != "N/A"
    
    if is_success:
        output_file = config.ACCOUNTS_WITH_API_KEY_FILE
        fieldnames = ["Email", "Password", "API_Key", "Timestamp"]
        row_data = {
            "Email": email, 
            "Password": password, 
            "API_Key": api_key,
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        output_file = config.FAILED_REGISTER_ACCOUNTS_FILE
        fieldnames = ["Email", "Status", "Timestamp"]
        row_data = {
            "Email": email, 
            "Status": status,
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    file_exists = os.path.exists(output_file)
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists or os.path.getsize(output_file) == 0:
            writer.writeheader()
        writer.writerow(row_data)
    
    logger.info(f"Đã lưu kết quả cho {email} vào file {os.path.basename(output_file)}")

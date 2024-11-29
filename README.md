# Hệ thống quản lý sự kiện hiến máu cho hội chữ thập đỏ

## Mô Tả

Sau khi tải ảnh lên, ứng dụng này sẽ quét hình ảnh để lấy những thông tin quan trọng như: số cccd, họ và tên.

---

## Cài Đặt

Để cài đặt dự án, bạn có thể tuân theo các bước sau:

1. **Clone Repository**: Sao chép repository từ GitHub về máy tính của bạn bằng cách chạy lệnh sau trong terminal:

   ```bash
   git clone https://github.com/longhoang123123/volunteer-ocr.git
   ```

2. **Cài lệnh uvicorn**:

   ```bash
   pip install uvicorn
   ```

3. **Chạy lệnh**:

   ```bash
   uvicorn app.main:main_app --port 8001 --reload
   ```

4. **Kiểm tra ứng dụng**:

   ```bash
   INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
   INFO:     Started reloader process [12345] using statreload
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)

   ```

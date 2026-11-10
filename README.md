# Shopee Transaction Analytics

Dashboard phân tích giao dịch Shopee chạy bằng Node.js, Express và JavaScript ở trình duyệt.

## Chạy trên máy cá nhân

Yêu cầu Node.js 18 trở lên.

```powershell
npm ci
npm start
```

Mở http://localhost:3000. Chọn dataset có sẵn từ danh sách hoặc tải file `.xlsx`, `.xls`, `.csv` lên để phân tích.

Nếu muốn server cung cấp dataset có sẵn, đặt các file trong thư mục dự án (cùng cấp với `server.js`). Các file Excel/CSV được `.gitignore` loại khỏi Git theo mặc định để tránh công khai dữ liệu giao dịch.

## Deploy online bằng Render

1. Tạo một repository GitHub. Nếu repository đặt **Public**, chỉ đẩy mã nguồn; không đẩy dữ liệu giao dịch thật, file `.env` hay dữ liệu khách hàng.
2. Cài [Git for Windows](https://git-scm.com/download/win), mở PowerShell tại thư mục dự án rồi chạy:

   ```powershell
   git init
   git add .gitignore README.md package.json package-lock.json render.yaml server.js public
   git commit -m "Prepare Shopee analytics app for deployment"
   git branch -M main
   git remote add origin https://github.com/<ten-tai-khoan>/<ten-repository>.git
   git push -u origin main
   ```

3. Trên [Render](https://render.com/), tạo **New > Blueprint** và kết nối repository vừa đẩy. Render đọc `render.yaml` để cài dependencies, chạy Express và kiểm tra `/api/health`.
4. Mở URL `.onrender.com` mà Render cấp. Dashboard sẽ dùng dữ liệu mô phỏng mặc định; người dùng có thể tải file dữ liệu của họ lên trình duyệt.

Gói Render miễn phí có thể đưa dịch vụ vào trạng thái ngủ khi không có truy cập; lần mở đầu tiên sau đó có thể mất thêm thời gian để khởi động.

## API

- `GET /api/health`: trạng thái dịch vụ.
- `GET /api/datasets`: danh sách dataset Excel/CSV có trong thư mục dự án.
- `GET /data/:filename`: tải một dataset được đặt trong thư mục dự án.
# Data

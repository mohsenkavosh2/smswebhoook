# SMS to Keyboard Webhook

تبدیل پیامک به کلیدهای کیبورد با استفاده از Webhook

## 🚀 تنظیمات سریع

### 1. Deploy روی Render
- این ریپازیتوری را Fork کنید
- به [render.com](https://render.com) بروید
- Web Service جدید ایجاد کنید
- ریپازیتوری را Connect کنید
- متغیرهای محیطی را تنظیم کنید

### 2. تنظیمات پنل پیامک
- Webhook URL: `https://your-app.onrender.com/webhook`
- Method: POST
- Format: JSON

### 3. اجرای سرور محلی
```bash
pip install flask pyautogui
python local_server.py

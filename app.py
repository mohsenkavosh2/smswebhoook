from flask import Flask, request
import os

app = Flask(__name__)

# کلیدواژه عددی پنل شما
KEYWORD = "123"  # همین عدد را در پنل وارد کنید

@app.route('/webhook', methods=['GET'])
def webhook():
    # دریافت همه پارامترها
    sender = request.args.get('from', '').strip()
    message = request.args.get('text', '').strip()
    to = request.args.get('to', '').strip()
    date = request.args.get('date', '')
    
    # لاگ کامل برای دیباگ
    print("=" * 60)
    print("📱 SMS WEBHOOK TRIGGERED")
    print(f"📞 From: {sender}")
    print(f"📝 Message: {message}")
    print(f"📨 To: {to}")
    print(f"📅 Date: {date}")
    print("=" * 60)
    
    # استخراج دستور از پیام
    # اگر پیام با کلیدواژه شروع شده، آن را حذف کن
    command = message
    if message.startswith(KEYWORD + " "):
        command = message[len(KEYWORD) + 1:].strip()
    elif message.startswith(KEYWORD):
        command = message[len(KEYWORD):].strip()
    
    print(f"🎯 Command extracted: '{command}'")
    
    # پاسخ بر اساس دستور
    responses = {
        "1": "✅ کلید S فشرده خواهد شد",
        "2": "✅ کلید Enter فشرده خواهد شد",
        "3": "✅ کلید Space فشرده خواهد شد",
        "test": "✅ تست موفق بود",
        "تست": "✅ تست فارسی موفق بود",
    }
    
    response = responses.get(command, f"✅ دستور '{command}' دریافت شد")
    
    # ذخیره لاگ
    with open("sms_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{date} | {sender} | {message} | {command} | {response}\n")
    
    return response, 200

@app.route('/logs', methods=['GET'])
def view_logs():
    """نمایش لاگ پیام‌های دریافتی"""
    try:
        with open("sms_log.txt", "r", encoding="utf-8") as f:
            logs = f.readlines()
        
        if not logs:
            return "<h3>هنوز هیچ پیامی دریافت نشده</h3>"
        
        html = "<h2>📱 تاریخچه پیام‌های دریافتی</h2><table border='1'><tr><th>تاریخ</th><th>فرستنده</th><th>پیام کامل</th><th>دستور</th><th>پاسخ</th></tr>"
        for log in logs[-20:]:  # ۲۰ پیام آخر
            parts = log.strip().split(" | ")
            if len(parts) >= 5:
                html += f"<tr><td>{parts[0]}</td><td>{parts[1]}</td><td>{parts[2]}</td><td>{parts[3]}</td><td>{parts[4]}</td></tr>"
        html += "</table>"
        return html
    except Exception as e:
        return f"خطا در خواندن لاگ: {str(e)}"

@app.route('/test', methods=['GET'])
def test_page():
    """صفحه تست"""
    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>تست وب‌هوک پیامک</title>
    </head>
    <body>
        <h2>🎯 تست سرویس پیامک</h2>
        
        <div style='background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;'>
            <h3>⚙️ تنظیمات پنل شما:</h3>
            <p><strong>پارامتر مورد بررسی:</strong> <code>{KEYWORD}</code></p>
            <p><strong>URL وب‌هوک:</strong></p>
            <code style='background: white; padding: 10px; display: block;'>
            https://smswebhoook.onrender.com/webhook?from=$FROM$&to=$TO$&text=$TEXT$&date=$DATETIME$
            </code>
        </div>
        
        <div style='background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;'>
            <h3>📱 نحوه استفاده:</h3>
            <ol>
                <li>در پنل پیامک، پارامتر مورد بررسی را <strong>{KEYWORD}</strong> قرار دهید</li>
                <li>URL بالا را در فیلد مربوطه وارد کنید</li>
                <li>کاربر پیامک می‌فرستد: <code>{KEYWORD} 1</code></li>
                <li>سیستم دستور <code>1</code> را اجرا می‌کند</li>
            </ol>
        </div>
        
        <h3>🧪 تست سریع:</h3>
        <p>روی لینک‌های زیر کلیک کنید (شبیه‌سازی ارسال پیامک):</p>
        <ul>
            <li><a href="/webhook?from=+989121234567&text={KEYWORD}%201&to=3000&date=2024-01-01">تست دستور 1 ({KEYWORD} 1)</a></li>
            <li><a href="/webhook?from=+989121234567&text={KEYWORD}%202&to=3000&date=2024-01-01">تست دستور 2 ({KEYWORD} 2)</a></li>
            <li><a href="/webhook?from=+989121234567&text={KEYWORD}%20test&to=3000&date=2024-01-01">تست دستور test ({KEYWORD} test)</a></li>
            <li><a href="/webhook?from=+989121234567&text={KEYWORD}%20تست&to=3000&date=2024-01-01">تست دستور تست ({KEYWORD} تست)</a></li>
        </ul>
        
        <p><a href="/logs">📊 مشاهده لاگ پیام‌ها</a></p>
    </body>
    </html>
    """

@app.route('/')
def home():
    return """
    <html>
    <head>
        <meta charset="utf-8">
        <title>سرویس وب‌هوک پیامک</title>
    </head>
    <body>
        <h1>✅ سرویس وب‌هوک پیامک فعال است</h1>
        <p>این سرویس برای اتصال پنل پیامک شما به کامپیوتر شخصی طراحی شده است.</p>
        
        <div style='background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <h2>🚀 وضعیت سرویس: <span style='color: green;'>فعال</span></h2>
            <p><a href='/test'>برو به صفحه تست و راهنمایی</a></p>
            <p><a href='/logs'>مشاهده لاگ پیام‌ها</a></p>
        </div>
        
        <h3>📞 پشتیبانی:</h3>
        <p>اگر مشکلی دارید:</p>
        <ol>
            <li>ابتدا از صفحه <a href='/test'>تست</a> استفاده کنید</li>
            <li>لاگ‌ها را بررسی کنید</li>
            <li>مطمئن شوید پنل شما به اینترنت متصل است</li>
        </ol>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SMS Webhook Service Started")
    print(f"🔢 Keyword/Parameter: {KEYWORD}")
    print("🌐 Server is running...")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000)

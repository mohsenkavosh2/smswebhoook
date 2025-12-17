from flask import Flask, request
import os

app = Flask(__name__)

# کلیدواژه پنل شما
KEYWORD = "cmd"

@app.route('/webhook', methods=['GET'])
def webhook():
    # دریافت داده از پنل
    sender = request.args.get('from', '')
    message = request.args.get('text', '')
    
    # فقط برای شماره شما (اگر خواستید محدود کنید)
    # if sender != "+989121234567":
    #     return "ERROR", 403
    
    # حذف کلیدواژه از ابتدای پیام
    if message.startswith(KEYWORD):
        command = message[len(KEYWORD):].strip()
    else:
        command = message.strip()
    
    # پردازش دستور
    if command == "1":
        # اینجا بعداً به کامپیوتر شما وصل می‌شود
        return "OK: کلید S فشرده شد"
    elif command == "2":
        return "OK: اینتر فشرده شد"
    elif command == "test":
        return "OK: تست موفق بود"
    else:
        return f"OK: دستور '{command}' دریافت شد"

@app.route('/')
def home():
    return f"""
    <h1>SMS Webhook</h1>
    <p>کلیدواژه: <strong>{KEYWORD}</strong></p>
    <p>مثال: کاربر پیامک می‌فرستد: <code>{KEYWORD} 1</code></p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

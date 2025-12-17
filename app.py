from flask import Flask, request, jsonify
import requests
import os
import logging
from urllib.parse import unquote

app = Flask(__name__)

# تنظیمات
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your-secret-key-here')
ALLOWED_NUMBERS = os.environ.get('ALLOWED_NUMBERS', '').split(',')
LOCAL_SERVER_URL = os.environ.get('LOCAL_SERVER_URL', '')
PANEL_CODE = os.environ.get('PANEL_CODE', '1234')  # کد پنل شما

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        # برای پنل‌های ایرانی (GET با پارامتر)
        if request.method == 'GET':
            # دریافت همه پارامترها
            sender = request.args.get('from', '')
            message = request.args.get('text', '')
            receiver = request.args.get('to', '')
            timestamp = request.args.get('date', '')
            code = request.args.get('code', request.args.get('password', request.args.get('api_key', '')))
            
            # لاگ همه پارامترها برای دیباگ
            logger.info(f"GET Params: {dict(request.args)}")
            
            # اگر کد پنل لازم است، بررسی کن
            if PANEL_CODE and code != PANEL_CODE:
                logger.warning(f"Invalid panel code: {code}")
                return "Invalid panel code", 403
            
            # decode متن اگر نیاز باشد
            if message:
                message = unquote(message)
            
        else:  # POST برای تست‌های دستی
            data = request.get_json() or {}
            sender = data.get('from', '')
            message = data.get('text', '').strip()
            timestamp = data.get('timestamp', data.get('date', ''))
            code = data.get('code', '')
        
        # بررسی وجود داده
        if not sender:
            return "Missing sender", 400
        
        if not message:
            message = "(empty)"
        
        logger.info(f"📱 SMS from {sender}: '{message}'")
        
        # بررسی شماره مجاز
        if ALLOWED_NUMBERS and sender.strip() not in [n.strip() for n in ALLOWED_NUMBERS if n]:
            logger.warning(f"❌ Unauthorized: {sender}")
            return "Unauthorized number", 403
        
        # پردازش پیام
        command = message.strip().lower()
        
        # اگر آدرس کامپیوتر محلی تنظیم شده
        if LOCAL_SERVER_URL:
            try:
                response = requests.post(
                    LOCAL_SERVER_URL,
                    json={
                        "command": command,
                        "sender": sender,
                        "auth": WEBHOOK_SECRET,
                        "timestamp": timestamp,
                        "original": message
                    },
                    timeout=5
                )
                
                logger.info(f"✅ Forwarded to local PC: {response.status_code}")
                
                # پاسخ به پنل
                return f"OK - Processed: {command}", 200
                
            except Exception as e:
                logger.error(f"❌ Local PC error: {str(e)}")
                return f"Processing queued - PC offline", 202
        
        # حالت تست (بدون اتصال به کامپیوتر)
        logger.info(f"🟡 Test mode - Would execute: {command}")
        
        # پاسخ ساده به پنل
        responses = {
            "1": "S key pressed",
            "2": "Enter pressed",
            "3": "Space pressed",
            "test": "Test successful",
            "hi": "Hello!",
            "سلام": "سلام! خوش آمدید"
        }
        
        action = responses.get(command, f"Command '{command}' received")
        return f"OK - {action}", 200
        
    except Exception as e:
        logger.error(f"🔥 Server error: {str(e)}")
        return f"Server Error: {str(e)}", 500

@app.route('/')
def home():
    return """
    <h1>SMS Webhook Service</h1>
    <p>Status: <span style='color:green;'>✅ Running</span></p>
    <p>Webhook URL for your panel:</p>
    <code>https://smswebhoook.onrender.com/webhook?code=1234&from=$FROM$&to=$TO$&text=$TEXT$&date=$DATETIME$</code>
    <p><a href='/health'>Health Check</a> | <a href='/test'>Test</a></p>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "webhook_url": "https://smswebhoook.onrender.com/webhook",
        "panel_code": PANEL_CODE,
        "allowed_numbers": ALLOWED_NUMBERS
    })

@app.route('/test')
def test():
    """صفحه تست برای بررسی کارکرد"""
    return """
    <h2>Test Webhook</h2>
    <form action="/webhook" method="GET">
        From: <input type="text" name="from" value="+989121234567"><br>
        Text: <input type="text" name="text" value="1"><br>
        To: <input type="text" name="to" value="+989123456789"><br>
        Date: <input type="text" name="date" value="2024-01-01"><br>
        Code: <input type="text" name="code" value="1234"><br>
        <input type="submit" value="Test">
    </form>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"🔑 Panel Code: {PANEL_CODE}")
    app.run(host='0.0.0.0', port=port)

from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# تنظیمات از متغیرهای محیطی
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your-secret-key-here')
ALLOWED_NUMBERS = os.environ.get('ALLOWED_NUMBERS', '').split(',')
LOCAL_SERVER_URL = os.environ.get('LOCAL_SERVER_URL', '')

# تنظیم لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # دریافت داده
        data = request.get_json()
        
        if not data:
            logger.warning("No data received")
            return jsonify({"error": "No data"}), 400
        
        # اعتبارسنجی
        sender = data.get('from', '')
        message = data.get('text', '').strip()
        
        logger.info(f"Received from {sender}: {message}")
        
        # بررسی شماره مجاز
        if ALLOWED_NUMBERS and sender not in ALLOWED_NUMBERS:
            logger.warning(f"Unauthorized number: {sender}")
            return jsonify({"error": "Unauthorized number"}), 403
        
        # اگر آدرس کامپیوتر محلی تنظیم شده
        if LOCAL_SERVER_URL:
            try:
                # ارسال به کامپیوتر محلی
                response = requests.post(
                    LOCAL_SERVER_URL,
                    json={
                        "command": message,
                        "sender": sender,
                        "auth": WEBHOOK_SECRET,
                        "timestamp": data.get('timestamp', '')
                    },
                    timeout=10  # افزایش تایم‌اوت
                )
                
                logger.info(f"Forwarded to local server: {response.status_code}")
                return jsonify({
                    "status": "forwarded",
                    "local_response": response.json() if response.content else {}
                })
                
            except requests.exceptions.Timeout:
                logger.error("Timeout connecting to local computer")
                return jsonify({"error": "Local computer timeout", "status": "pending"}), 202
            except requests.exceptions.ConnectionError:
                logger.error("Cannot connect to local computer")
                return jsonify({"error": "Local computer offline", "status": "pending"}), 202
            except Exception as e:
                logger.error(f"Local server error: {str(e)}")
                return jsonify({"error": f"Local error: {str(e)}"}), 502
        
        # اگر آدرس محلی تنظیم نشده (حالت تست)
        return jsonify({
            "status": "test_mode",
            "message": f"Command '{message}' from {sender} received but not forwarded",
            "note": "Set LOCAL_SERVER_URL in environment variables"
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "sms-webhook-proxy",
        "local_server_configured": bool(LOCAL_SERVER_URL)
    })

@app.route('/test', methods=['GET'])
def test():
    """Endpoint for testing"""
    return jsonify({
        "message": "SMS Webhook is running",
        "endpoints": {
            "webhook": "POST /webhook",
            "health": "GET /health"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

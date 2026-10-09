#!/usr/bin/env python3
import datetime
import urllib.request
import urllib.error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# قائمة الخدمات المراد مراقبتها
ENDPOINTS = [
    {"name": "Local Web App", "url": "http://localhost:8080"},
    {"name": "GitHub Profile", "url": "https://github.com"},
    {"name": "Google Search", "url": "https://www.google.com"}
]

INCIDENT_LOG_FILE = "incident.log"

# إعدادات البريد الإلكتروني (يمكنك استبدالها ببياناتك الحقيقية لاحقاً)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # كلمة مرور التطبيقات من إعدادات جوجل
RECEIVER_EMAIL = "target_email@gmail.com"

def send_alert_email(service_name, error_message):
    try:
        subject = f"[CRITICAL ALERT] Service Down: {service_name}"
        body = f"Hello SRE Team,\n\nThe following service has failed:\nService: {service_name}\nError: {error_message}\nTime: {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n\nPlease take immediate action."
        
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        # الاتصال بخادم البريد وإرسال الرسالة
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            
        print(f"[EMAIL SENT] Alert email sent successfully for: {service_name}")
    except Exception as e:
        print(f"[EMAIL FAILED] Could not send email: {e}")

def log_incident(service_name, error_message):
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    log_entry = f"[{timestamp}] [CRITICAL] Service Down: {service_name} - Reason: {error_message}\n"
    
    # كتابة الحادثة في ملف السجلات المركزي
    with open(INCIDENT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"[ALERT LOGGED] Recorded incident for: {service_name}")
    
    # إرسال إيميل تنبيهي عند حدوث العطل
    # send_alert_email(service_name, error_message)

def check_and_respond(endpoint):
    try:
        req = urllib.request.Request(
            endpoint["url"],
            headers={"User-Agent": "SRE-IncidentResponder/1.0"}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                print(f"[UP] {endpoint['name']} is healthy")
                return True
    except Exception as e:
        error_msg = str(e)
        print(f"[DOWN] {endpoint['name']} failed: {error_msg}")
        log_incident(endpoint["name"], error_msg)
    return False

if __name__ == "__main__":
    print("=== Starting Automated Incident Response Pipeline ===")
    for endpoint in ENDPOINTS:
        check_and_respond(endpoint)
    print("=== Pipeline Execution Complete ===")
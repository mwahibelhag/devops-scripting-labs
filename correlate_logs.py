#!/usr/bin/env python3
import json
import os
import sys

# الخدمات المصغرة التي سنراقب سجلاتها
SERVICES = ["auth", "ledger", "notification"]
LOG_DIR = "./logs"

def load_and_correlate(trace_id):
    matched_lines = []
    seen_services = set()
    
    # التأكد من وجود مجلد السجلات
    if not os.path.exists(LOG_DIR):
        print(f"[ERROR] Log directory '{LOG_DIR}' not found. Please create it and add service logs.")
        return

    for service in SERVICES:
        log_file = os.path.join(LOG_DIR, f"{service}.log")
        if not os.path.exists(log_file):
            continue
        with open(log_file) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    if data.get("trace_id") == trace_id:
                        data["_source"] = service
                        matched_lines.append(data)
                        seen_services.add(service)
                except json.JSONDecodeError:
                    print(f"[WARNING] Non-JSON log in {service}.log line {line_num}: {line.strip()[:80]}")

    # ترتيب السجلات زمنياً بناءً على الـ timestamp
    matched_lines.sort(key=lambda x: x.get("timestamp", ""))
    
    print(f"\n=== Timeline for Trace ID: {trace_id} ===")
    if not matched_lines:
        print("[INFO] No logs found for this Trace ID.")
    for item in matched_lines:
        print(f"[{item.get('timestamp')}] [{item['_source'].upper()}] [{item.get('level', 'INFO')}] {item.get('event')}")
        
    # فحص الخدمات المفقودة التي لم تسجل هذا المعرف
    missing = set(SERVICES) - seen_services
    if missing:
        print(f"\n[MISSING TELEMETRY] No trace-tagged logs from: {', '.join(missing)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        load_and_correlate(sys.argv[1])
    else:
        print("Usage: python correlate_logs.py <trace_id>")
        
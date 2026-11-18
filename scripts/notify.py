#!/usr/bin/env python3
"""Post-build e-mail (standard library only). Configuration comes from env vars set by Jenkins.

SMTP_USER / SMTP_PASS : sender account (Gmail address + app password) - the From address
MAIL_TO               : recipient (default qasimalik@gmail.com)
STATUS, BUILD_NUMBER, BUILD_URL, GIT_COMMIT, JOB_NAME : build info
"""
import json
import os
import smtplib
import sys
import time
import urllib.request
from email.message import EmailMessage

REG = "FA23-BDS-057"
TO = os.environ.get("MAIL_TO", "qasimalik@gmail.com")
USER = os.environ["SMTP_USER"]
PASSWORD = os.environ["SMTP_PASS"].replace(" ", "")
STATUS = os.environ.get("STATUS", "UNKNOWN")
HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")


def live_metrics():
    try:
        with urllib.request.urlopen("http://localhost:8000/metrics", timeout=5) as r:
            return json.loads(r.read())
    except Exception as exc:  # noqa: BLE001
        return {"error": f"/metrics not reachable: {exc}"}


def build_message():
    metrics = live_metrics()
    msg = EmailMessage()
    msg["From"] = USER
    msg["To"] = TO
    msg["Subject"] = f"[MIDTERM] {REG} - Build #{os.environ.get('BUILD_NUMBER', '?')} {STATUS}"
    msg.set_content(
        f"Student Reg No: {REG}\n"
        f"Job: {os.environ.get('JOB_NAME', 'MIDTERM-' + REG)}  build #{os.environ.get('BUILD_NUMBER', '?')}\n"
        f"Result: {STATUS}\n"
        f"Commit: {os.environ.get('GIT_COMMIT', 'unknown')}\n"
        f"Author: {os.environ.get('AUTHOR_NAME', '?')} <{os.environ.get('AUTHOR_EMAIL', '?')}>\n"
        f"Build URL: {os.environ.get('BUILD_URL', '-')}\n"
        f"Metrics URL: http://16.16.10.42:8000/metrics\n\n"
        f"Live /metrics:\n{json.dumps(metrics, indent=2)}\n"
    )
    return msg


def send(msg):
    last = None
    for attempt in range(1, 4):
        try:
            if attempt == 3:  # last try over implicit TLS
                with smtplib.SMTP_SSL(HOST, 465, timeout=30) as s:
                    s.login(USER, PASSWORD)
                    s.send_message(msg)
            else:
                with smtplib.SMTP(HOST, 587, timeout=30) as s:
                    s.starttls()
                    s.login(USER, PASSWORD)
                    s.send_message(msg)
            print(f"mail sent from {USER} to {TO}")
            return 0
        except Exception as exc:  # noqa: BLE001
            last = exc
            print(f"attempt {attempt} failed: {exc}", file=sys.stderr)
            time.sleep(3)
    print(f"could not send mail: {last}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(send(build_message()))

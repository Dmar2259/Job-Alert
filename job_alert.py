import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from datetime import datetime

# ============================
# CONFIGURATION
# ============================

SEND_FROM = "jackdemarrr@icloud.com"
SEND_TO = "douggmonroe@gmail.com"
SMTP_SERVER = "smtp.mail.me.com"
SMTP_PORT = 587
SMTP_PASSWORD = os.getenv("ICLOUD_APP_PASSWORD")  # GitHub Secret

JOB_SITES = [
    "https://www.indeed.co.uk/jobs?q=customer+service&l=Essex",
    "https://www.indeed.co.uk/jobs?q=customer+service&l=London",
    "https://www.indeed.co.uk/jobs?q=customer+service&l=Edinburgh",
    "https://www.indeed.co.uk/jobs?q=customer+service&l=Glasgow",
    "https://www.indeed.co.uk/jobs?q=customer+service&l=Dundee",
    "https://www.indeed.co.uk/jobs?q=customer+service&l=Aberdeen",
    "https://www.indeed.co.uk/jobs?q=customer+service&l=Remote"
]

TITLE_KEYWORDS = [
    "customer service", "call centre", "contact centre",
    "customer support", "customer care", "inbound", "advisor", "agent"
]

BULK_HIRE_KEYWORDS = [
    "multiple vacancies", "mass recruitment", "bulk intake",
    "large intake", "several positions", "expanding team",
    "high-volume", "training academy", "assessment centre"
]

SEEN_FILE = "seen_jobs.json"
# ============================


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def fetch_jobs():
    jobs = []
    for url in JOB_SITES:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                jobs.append((url, r.text))
        except:
            pass
    return jobs


def extract_jobs(html):
    # Simple extraction — GitHub Actions can run this reliably
    results = []
    lines = html.split("\n")
    for line in lines:
        if "jobTitle" in line.lower():
            results.append(line.strip())
    return results


def matches_title(text):
    text = text.lower()
    return any(k in text for k in TITLE_KEYWORDS)


def is_bulk_hire(text):
    text = text.lower()
    return any(k in text for k in BULK_HIRE_KEYWORDS)


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SEND_FROM
    msg["To"] = SEND_TO
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SEND_FROM, SMTP_PASSWORD)
        server.sendmail(SEND_FROM, SEND_TO, msg.as_string())


def main():
    seen = load_seen()
    jobs_found = []

    for url, html in fetch_jobs():
        extracted = extract_jobs(html)
        for job in extracted:
            if not matches_title(job):
                continue

            job_id = f"{url}-{job}"

            if job_id in seen:
                continue

            seen.add(job_id)

            priority = is_bulk_hire(job)
            jobs_found.append((job, url, priority))

    save_seen(seen)

    for job, url, priority in jobs_found:
        if priority:
            subject = f"HIGH PRIORITY — Bulk Hiring Detected"
        else:
            subject = f"New Job Alert"

        body = f"Job: {job}\nSource: {url}\nTime: {datetime.now()}"
        send_email(subject, body)


if __name__ == "__main__":
    main()

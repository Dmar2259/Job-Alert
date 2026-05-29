import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

KEYWORDS = [
    "customer service",
    "customer support",
    "HR administrator",
    "sales customer support",
    "gallery attendant",
    "warehouse",
    "production worker",
    "traffic warden",
    "royal mail sorter"
]

SEARCH_URL = "https://www.reed.co.uk/api/1.0/search"
API_KEY = ""  # Optional: only needed if you use Reed API keys

SENDER_EMAIL = "jackdemarrr@icloud.com"
RECEIVER_EMAIL = "douggmonroe@gmail.com"
ICLOUD_APP_PASSWORD = "WILL_BE_IN_ENV_VARIABLE"

SEEN_JOBS_FILE = "seen_jobs.txt"


# -----------------------------------------
# LOAD SEEN JOBS
# -----------------------------------------

def load_seen_jobs():
    try:
        with open(SEEN_JOBS_FILE, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()


def save_seen_job(job_id):
    with open(SEEN_JOBS_FILE, "a") as f:
        f.write(job_id + "\n")


# -----------------------------------------
# SEARCH JOBS
# -----------------------------------------

def search_jobs(keyword):
    params = {
        "keywords": keyword,
        "location": "Essex",
        "distancefromlocation": 25
    }

    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Basic {API_KEY}"

    response = requests.get(SEARCH_URL, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching jobs for '{keyword}': {response.status_code}")
        return []

    data = response.json()
    return data.get("results", [])


# -----------------------------------------
# SEND EMAIL
# -----------------------------------------

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.mail.me.com", 587) as server:
        server.login(SENDER_EMAIL, ICLOUD_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())


# -----------------------------------------
# MAIN LOGIC
# -----------------------------------------

def main():
    seen_jobs = load_seen_jobs()
    new_jobs_found = False

    send_email("Test Email", "This is a test email from your GitHub Action.")
    print("Test email sent.")
    return


    for keyword in KEYWORDS:
        print(f"Searching for: {keyword}")
        jobs = search_jobs(keyword)

        for job in jobs:
            job_id = str(job.get("jobId"))

            if job_id in seen_jobs:
                continue

            seen_jobs.add(job_id)
            save_seen_job(job_id)
            new_jobs_found = True

            title = job.get("jobTitle", "No title")
            company = job.get("employerName", "Unknown company")
            location = job.get("locationName", "Unknown location")
            url = job.get("jobUrl", "No URL")

            email_body = (
                f"New job found:\n\n"
                f"Title: {title}\n"
                f"Company: {company}\n"
                f"Location: {location}\n"
                f"URL: {url}\n"
            )

            send_email(f"New Job Alert: {title}", email_body)
            print(f"Sent alert for: {title}")

    if not new_jobs_found:
        print("No new jobs found.")


if __name__ == "__main__":
    main()

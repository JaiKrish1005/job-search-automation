import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

queries = [
    "Entry level SDE 1 jobs site:wellfound.com",
    "Entry level Solution Engineer jobs site:wellfound.com",
    "Entry level Low code Developer jobs site:wellfound.com"
]

LOG_FILE = "job_log.txt"

def fetch_job_links(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.bing.com/search?q={requests.utils.quote(query)}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for h2 in soup.find_all("h2"):
        a = h2.find("a")
        if a and a["href"].startswith("http"):
            links.append((a.text.strip(), a["href"]))
        if len(links) >= 5:
            break

    return links

def load_logged_links():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_logged_links(new_links):
    with open(LOG_FILE, "a") as f:
        for link in new_links:
            f.write(link + "\n")

def send_email(subject, body):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    receiver = os.environ["EMAIL_RECEIVER"]

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

def main():
    seen_links = load_logged_links()
    all_new_links = []
    body = f"Job Digest - {datetime.now().strftime('%B %d, %Y, %I:%M %p')}\n\n"

    for query in queries:
        body += f"{query}\n"
        results = fetch_job_links(query)
        new_results = [(title, link) for title, link in results if link not in seen_links]

        if not new_results:
            body += "No new jobs found.\n\n"
            continue

        for title, link in new_results:
            body += f"- {title}\n  {link}\n"
            all_new_links.append(link)
        body += "\n"

    if all_new_links:
        send_email("Job Search Update", body)
        save_logged_links(all_new_links)
        print(f"Sent {len(all_new_links)} new job(s).")
    else:
        print("No new jobs to send.")

if __name__ == "__main__":
    main()

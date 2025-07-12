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
    body = f"Daily Job Digest - {datetime.now().strftime('%B %d, %Y')}\n\n"

    for query in queries:
        body += f" {query}\n"
        results = fetch_job_links(query)
        for title, link in results:
            body += f"- {title}\n  {link}\n"
        body += "\n"

    send_email("Daily Job Search Results", body)

if __name__ == "__main__":
    main()

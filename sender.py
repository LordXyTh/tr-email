import smtplib
import sqlite3
import random
import json
import logging
from email.mime.text import MIMEText
from email.header import Header
import time
import sys


DATABASE_NAME = "/home/ubuntu/tr-email/emails.db"
LIMIT_PER_SENDER = 3
EMAIL_TEMPLATE_FILE = "/home/ubuntu/tr-email/email_templates.json"
SUBJECT_TEMPLATE_FILE = "/home/ubuntu/tr-email/subject_templates.json"
CANNABIS_TEMPLATES_FILE = "/home/ubuntu/tr-email/cannabis_templates.json"
BCC_EMAIL = "hello@liberv.community"
MAX_EMAIL = 20
def load_email_templates():
    with open(EMAIL_TEMPLATE_FILE, 'r') as file:
        return json.load(file)

def load_subject_templates():
    with open(SUBJECT_TEMPLATE_FILE, 'r') as file:
        return json.load(file)

def load_cannabis_templates():
    with open(CANNABIS_TEMPLATES_FILE, 'r') as file:
        return json.load(file)

def get_random_template(templates):
    return random.choice(list(templates.values()))

def get_random_subject(subjects):
    return random.choice(list(subjects.values()))

def get_cannabis_template(templates):
    random_key = random.choice(list(templates.keys()))
    return random_key, templates[random_key]

def get_target_emails(sender_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT email FROM target_emails WHERE id NOT IN 
    (SELECT target_id FROM sent_log WHERE sender_id=?)""", (sender_id,))

    emails = cursor.fetchall()
    conn.close()
    return [email[0] for email in emails]

def get_sender_emails():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, email, password FROM sender_emails")
    credentials = cursor.fetchall()

    conn.close()
    return credentials

def mark_email_as_sent(sender_id, target_email):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM target_emails WHERE email=?", (target_email,))
    target_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO sent_log (sender_id, target_id) VALUES (?, ?)", (sender_id, target_id))
    conn.commit()
    conn.close()

def send_emails():
    print("getting credentials")
    sender_credentials = get_sender_emails()
    print(f"I got credentials {sender_credentials}")
    email_templates = load_email_templates()
    subject_templates = load_subject_templates()
    cannabis_templates = load_cannabis_templates()
    emails_sent = 0
    for sender_id, sender_email, sender_password in sender_credentials:
        target_emails = get_target_emails(sender_id)
        selected_targets = random.sample(target_emails, min(LIMIT_PER_SENDER, len(target_emails)))
        mail_server = "mail."+sender_email.split("@")[1]
        if sender_email.split("@")[1] == "vogt-tabak.de":
            continue
        try:
            with smtplib.SMTP(mail_server, 587) as server:  # Replace with your SMTP server
                server.starttls()
                print(sender_email, sender_password)
                server.login(sender_email, sender_password)

                for target_email in selected_targets:
                    if emails_sent >= MAX_EMAIL:
                        sys.exit(0)
                    if random.choice([True, False]):
                        email_content = get_random_template(email_templates)
                        subject = get_random_subject(subject_templates)
                    else:
                        subject, email_content = get_cannabis_template(cannabis_templates)
                    
                    # Replace the {{ variable }} with any appropriate content
                    email_content = email_content.replace("{{name}}", "SomeContent")
                    
                    # Construct the MIMEText email
                    msg = MIMEText(email_content, 'plain', 'utf-8')
                    msg['Subject'] = Header(subject, 'utf-8')
                    msg['From'] = sender_email
                    msg['To'] = target_email
                    print(f"using {email_content} as msg")
                    server.sendmail(sender_email, [target_email, BCC_EMAIL], msg.as_string())
                
                    print(f"sent mail from {sender_email} to {target_email}")
                    mark_email_as_sent(sender_id, target_email)
                    emails_sent += 1
        except Exception as e:
            print(f"error {e}")
            continue

if __name__ == "__main__":
    print("sending")
    send_emails()

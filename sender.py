import smtplib
import sqlite3
import random
import json
import logging
from email.mime.text import MIMEText
from email.header import Header
import time


DATABASE_NAME = "emails.db"
LIMIT_PER_SENDER = 100
EMAIL_TEMPLATE_FILE = "email_templates.json"
SUBJECT_TEMPLATE_FILE = "subject_templates.json"
BCC_EMAIL = "hello@liberv.community"
def load_email_templates():
    with open(EMAIL_TEMPLATE_FILE, 'r') as file:
        return json.load(file)

def load_subject_templates():
    with open(SUBJECT_TEMPLATE_FILE, 'r') as file:
        return json.load(file)

def get_random_template(templates):
    return random.choice(list(templates.values()))

def get_random_subject(subjects):
    return random.choice(list(subjects.values()))

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
    sender_credentials = get_sender_emails()
    logging.info(f"I got credentials {sender_credentials}")
    email_templates = load_email_templates()
    subject_templates = load_subject_templates()

    for sender_id, sender_email, sender_password in sender_credentials:
        target_emails = get_target_emails(sender_id)
        selected_targets = random.sample(target_emails, min(LIMIT_PER_SENDER, len(target_emails)))
        mail_server = "mail."+sender_email.split("@")[1]
        print(mail_server)
        with smtplib.SMTP(mail_server, 587) as server:  # Replace with your SMTP server
            server.starttls()
            print(sender_email, sender_password)
            server.login(sender_email, sender_password)

            for target_email in selected_targets:
                email_content = get_random_template(email_templates)
                subject = get_random_subject(subject_templates)
                
                # Replace the {{ variable }} with any appropriate content
                email_content = email_content.replace("{{name}}", "SomeContent")
                
                # Construct the MIMEText email
                msg = MIMEText(email_content, 'plain', 'utf-8')
                msg['Subject'] = Header(subject, 'utf-8')
                msg['From'] = sender_email
                msg['To'] = target_email
                
                server.sendmail(sender_email, [target_email, BCC_EMAIL], msg.as_string())
                
                print("sent")
                mark_email_as_sent(sender_id, target_email)
                

if __name__ == "__main__":
    print("sending")
    send_emails()

if __name__ == "__main__":
    print("sending")
    send_emails()

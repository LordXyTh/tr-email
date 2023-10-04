import smtplib
import sqlite3
import random
import json
import logging

DATABASE_NAME = "emails.db"
LIMIT_PER_SENDER = 100
EMAIL_TEMPLATE_FILE = "email_templates.json"

def load_email_templates():
    with open(EMAIL_TEMPLATE_FILE, 'r') as file:
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

    for sender_id, sender_email, sender_password in sender_credentials:
        target_emails = get_target_emails(sender_id)
        selected_targets = random.sample(target_emails, min(LIMIT_PER_SENDER, len(target_emails)))
        with smtplib.SMTP('mail.familiebeyermann.de', 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            print(sender_email)
            print(sender_password)

            for target_email in selected_targets:
                email_content = get_random_template(email_templates)
                # Here you can replace the {{ variable }} with any appropriate content
                email_content = email_content.replace("{{name}}", "SomeContent")
                
                server.sendmail(sender_email, target_email, f"Subject: Test Email\n\n{email_content}")
                print("sent")
                mark_email_as_sent(sender_id, target_email)

if __name__ == "__main__":
    print("sending")
    send_emails()

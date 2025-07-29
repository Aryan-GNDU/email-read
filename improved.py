import imaplib
import email
from email.header import decode_header
import os
import json
import re
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Load .env variables
load_dotenv()
username = os.getenv("EMAIL")
app_password = os.getenv("app_pass")
imap_server = "imap.gmail.com"
FILTER_SUBJECT = os.getenv("FILTER_SUBJECT") or input("Enter subject to filter by: ")

# Decode MIME-encoded words
def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return "".join(part.decode(enc or "utf-8") if isinstance(part, bytes) else part for part, enc in decoded)

# Normalize subject for thread grouping
def normalize_subject(subject):
    return re.sub(r"^(Re:|Fwd:|FW:)\s*", "", subject.strip(), flags=re.IGNORECASE)

# Determine email type
def determine_type(subject, msg):
    subj = subject.lower()
    if "in-reply-to" in msg:
        return "reply"
    elif subj.startswith("re:"):
        return "reply"
    elif subj.startswith("fwd:") or subj.startswith("fw:"):
        return "forward"
    else:
        return "new"

# Create folder-safe names
def safe_folder_name(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)[:50]

# IMAP Setup
imap = imaplib.IMAP4_SSL(imap_server)
imap.login(username, app_password)

# Output data
threads = defaultdict(list)
attachment_base = Path("attachments")
attachment_base.mkdir(exist_ok=True)

# Mailboxes
for mailbox in ["INBOX", "[Gmail]/Sent Mail"]:
    imap.select(f'"{mailbox}"')

    status, messages = imap.search(None, f'(SUBJECT "{FILTER_SUBJECT}")')
    if status != "OK":
        continue

    email_ids = messages[0].split()
    print(f" {len(email_ids)} emails in '{mailbox}'")

    for i, email_id in enumerate(email_ids):
        _, msg_data = imap.fetch(email_id, "(RFC822)")
        raw_msg = msg_data[0][1]
        msg = email.message_from_bytes(raw_msg)

        subject_raw = decode_mime_words(msg.get("Subject", ""))
        subject_normalized = normalize_subject(subject_raw)
        email_type = determine_type(subject_raw, msg)

        sender = decode_mime_words(msg.get("From", ""))
        recipient = decode_mime_words(msg.get("To", ""))
        date = msg.get("Date", "")
        message_id = msg.get("Message-ID", "")
        in_reply_to = msg.get("In-Reply-To", "")
        references = msg.get("References", "")
        body = ""
        attachments = []

        # Attachment folder
        thread_folder = attachment_base / safe_folder_name(subject_normalized)
        email_folder = thread_folder / f"{len(threads[subject_normalized])}"
        email_folder.mkdir(parents=True, exist_ok=True)

        # Extract body and attachments
        for part in msg.walk():
            content_disposition = str(part.get("Content-Disposition") or "")
            content_type = part.get_content_type()
            if content_type == "text/plain" and "attachment" not in content_disposition:
                charset = part.get_content_charset() or "utf-8"
                try:
                    body += part.get_payload(decode=True).decode(charset, errors="ignore")
                except:  # noqa: E722
                    continue
            elif "attachment" in content_disposition:
                filename = decode_mime_words(part.get_filename())
                if filename:
                    filepath = email_folder / filename
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    attachments.append(filename)

        # Append to thread
        threads[subject_normalized].append({
            "Type": email_type,
            "ReplyTo": in_reply_to or references or None,
            "From": sender,
            "To": recipient,
            "Date": date,
            "Body": body.strip(),
            "Attachments": attachments,
            "AttachmentFolder": str(email_folder)
        })

imap.close()
imap.logout()

# Sort emails in each thread by date
for msgs in threads.values():
    msgs.sort(key=lambda m: datetime.strptime(m["Date"], "%a, %d %b %Y %H:%M:%S %z") if m["Date"] else datetime.min)

# Prepare final JSON
threaded_output = [{"Thread": subj, "Messages": msgs} for subj, msgs in threads.items()]

# Save to JSON
with open("threaded_emails.json", "w", encoding="utf-8") as f:
    json.dump(threaded_output, f, indent=2, ensure_ascii=False)

print("\n Emails grouped, attachments saved, and JSON exported to 'threaded_emails.json'.")
try:
    # code that might raise an exception
    pass
except Exception as e:
    print(f"An error occurred: {e}")

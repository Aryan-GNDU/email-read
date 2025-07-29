import imaplib
import email
from email.header import decode_header
import csv


def extract_emails_by_subject(
    email_address, app_password, subject_filter, output_file="filtered_emails.csv"
):
    def decode_mime_words(s):
        if not s:
            return ""
        decoded = decode_header(s)
        return "".join(
            part.decode(enc or "utf-8") if isinstance(part, bytes) else part
            for part, enc in decoded
        )

    imap_server = "imap.gmail.com"
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_address, app_password)

    emails_data = []

    for mailbox in ["INBOX", "[Gmail]/Sent Mail"]:
        status, _ = imap.select(f'"{mailbox}"')
        if status != "OK":
            print(f"Could not open mailbox: {mailbox}")
            continue

        status, messages = imap.search(None, f'(SUBJECT "{subject_filter}")')
        if status != "OK":
            print(f"No emails found in {mailbox}.")
            continue

        email_ids = messages[0].split()
        print(
            f" Found {len(email_ids)} emails in {mailbox} with subject '{subject_filter}'"
        )

        for email_id in email_ids:
            _, msg_data = imap.fetch(email_id, "(RFC822)")
            raw_msg = msg_data[0][1]
            msg = email.message_from_bytes(raw_msg)

            subject = decode_mime_words(msg["Subject"])
            sender = decode_mime_words(msg.get("From", ""))
            to = decode_mime_words(msg.get("To", ""))
            date = msg.get("Date", "")
            body = ""
            attachments = []

            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition") or "")
                if (
                    part.get_content_type() == "text/plain"
                    and "attachment" not in content_disposition
                ):
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        body += part.get_payload(decode=True).decode(
                            charset, errors="ignore"
                        )
                    except Exception:
                        pass
                elif "attachment" in content_disposition:
                    filename = decode_mime_words(part.get_filename())
                    if filename:
                        attachments.append(filename)

            emails_data.append(
                {
                    "Mailbox": mailbox,
                    "Subject": subject,
                    "From": sender,
                    "To": to,
                    "Date": date,
                    "Body": body.strip(),
                    "Attachments": ", ".join(attachments),
                }
            )

    imap.close()
    imap.logout()

    # Save to CSV
    with open(output_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Mailbox",
                "Subject",
                "From",
                "To",
                "Date",
                "Body",
                "Attachments",
            ],
        )
        writer.writeheader()
        writer.writerows(emails_data)

    print(f"\nExtracted {len(emails_data)} emails. Saved to '{output_file}'.")


#  Example usage
if __name__ == "__main__":
    email_address = input("Enter your email: ")
    app_password = input("Enter your app password: ")
    subject_filter = input("Enter subject to filter by: ")

    extract_emails_by_subject(email_address, app_password, subject_filter)

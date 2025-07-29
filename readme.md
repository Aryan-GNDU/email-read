# 📬 Email Thread Extractor & Attachment Organizer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![IMAP](https://img.shields.io/badge/IMAP-Gmail-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A powerful Python script to **extract, group, and save Gmail emails and attachments** by conversation thread. Export your emails to a clean, organized JSON file and keep all attachments neatly sorted by thread and message.

---

## ✨ Features

- 🔑 **Secure Gmail login** using `.env` for credentials
- 🔎 **Filter emails by subject** (via prompt or env variable)
- 🧵 **Group emails into threads** (ignores "Re:", "Fwd:", etc.)
- 📎 **Extract and save all attachments** in organized folders
- 📝 **Export all data to a readable JSON file**
- 🕒 **Sort emails in each thread by date**
- 💡 **Easy to use, no code changes needed**

---

## 🚀 Quick Start

1. **Clone this repo & install dependencies**
    ```sh
    git clone https://github.com/yourusername/email-thread-extractor.git
    cd email-thread-extractor
    pip install python-dotenv
    ```

2. **Create a `.env` file** in the project root:
    ```
    EMAIL=your_email@gmail.com
    app_pass=your_gmail_app_password
    FILTER_SUBJECT=Optional subject filter
    ```

    > 💡 [How to get a Gmail App Password?](https://support.google.com/accounts/answer/185833?hl=en)

3. **Run the script**
    ```sh
    python improved.py
    ```

4. **Check your output**
    - Attachments saved in the `attachments/` folder, organized by thread and message
    - All email data exported to `threaded_emails.json`

---

## 📂 Output Structure

```
attachments/
  ├─ Thread_Subject_1/
  │    ├─ 0/
  │    │   └─ file1.pdf
  │    └─ 1/
  │        └─ image.png
  └─ Thread_Subject_2/
       └─ 0/
           └─ doc.docx

threaded_emails.json
```

---

## 🛠️ How It Works

- **Connects to Gmail** via IMAP using credentials from `.env`
- **Searches INBOX and Sent Mail** for emails matching your subject filter
- **Normalizes subjects** to group related emails (ignores "Re:", "Fwd:", etc.)
- **Extracts plain text bodies** and saves all attachments
- **Organizes attachments** into folders by thread and message
- **Exports all threads and messages** to a single JSON file

---

## ⚠️ Notes

- **App Password Required:** For Gmail, you must use an [App Password](https://support.google.com/accounts/answer/185833?hl=en) (not your regular password).
- **Privacy:** Your credentials are loaded from `.env` and never stored in code.
- **Error Handling:** The script prints any errors encountered during execution.

---

## 📜 License

This project is licensed under the MIT License.

---

## 🤝 Contributions

Pull requests, issues, and suggestions are welcome!  
If you find this useful, please ⭐️ the repo!

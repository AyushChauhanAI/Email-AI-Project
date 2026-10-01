# """
# test_gmail_connection.py
# Sirf ye check karta hai ki Gmail IMAP se connect ho raha hai ya nahi,
# aur kitne unread (naye) emails hain. AI/Groq abhi involve nahi hai.
# """

# import imaplib
# import os
# from dotenv import load_dotenv

# # .env file se GMAIL_USER aur GMAIL_APP_PASSWORD load karo
# load_dotenv()

# GMAIL_USER = os.getenv("GMAIL_USER")
# GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


# def test_connection():
#     if not GMAIL_USER or not GMAIL_APP_PASSWORD:
#         print("❌ .env file mein GMAIL_USER ya GMAIL_APP_PASSWORD nahi mil raha.")
#         print("   Check karo .env file isi folder mein hai aur naam sahi hai.")
#         return

#     try:
#         print(f"🔌 Connecting to Gmail ({GMAIL_USER}) ...")

#         # Gmail ka IMAP server, SSL ke sath, port 993 (fixed hai, hamesha yahi)
#         mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)

#         # Login karo App Password se
#         mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
#         print("✅ Login successful!")

#         # Inbox select karo
#         mail.select("inbox")

#         # Sirf UNSEEN (unread / naye) emails search karo
#         status, messages = mail.search(None, "UNSEEN")
#         unread_ids = messages[0].split()

#         print(f"📬 Total unread emails: {len(unread_ids)}")

#         # Pehle 5 unread emails ka subject + sender dikhao
#         # BODY.PEEK use kiya hai taaki email "read" mark na ho jaye
#         for eid in unread_ids[:5]:
#             status, data = mail.fetch(eid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
#             header = data[0][1].decode(errors="ignore").strip()
#             print("-" * 50)
#             print(header)

#         mail.logout()
#         print("\n✅ Test complete — Gmail connection sahi kaam kar raha hai!")

#     except imaplib.IMAP4.error as e:
#         print(f"❌ Login fail hua: {e}")
#         print("   Check karo: App Password sahi copy kiya (bina spaces ke)?")
#         print("   2-Step Verification ON hai account mein?")
#     except Exception as e:
#         print(f"❌ Kuch error aaya: {e}")


# if __name__ == "__main__":
#     test_connection()



"""
test_gmail_connection.py
Gmail se connect karke sirf sabse LATEST (naya) unread email print karta hai
- subject/from properly decode karke (encoded gibberish nahi)
- body ka preview bhi dikhata hai
"""

import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def decode_str(value):
    """MIME-encoded headers (=?UTF-8?...?=) ko readable text mein convert karta hai."""
    if not value:
        return ""
    parts = decode_header(value)
    result = ""
    for part, encoding in parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result


def get_email_body(msg):
    """Email se plain text body nikalta hai (multipart ho ya simple, dono handle karta hai)."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="ignore")
        return "(Plain text body nahi mila — shayad sirf HTML email hai)"
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="ignore") if payload else ""


def test_connection():
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("❌ .env file mein GMAIL_USER ya GMAIL_APP_PASSWORD nahi mil raha.")
        return

    try:
        print(f"🔌 Connecting to Gmail ({GMAIL_USER}) ...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        print("✅ Login successful!")

        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        unread_ids = messages[0].split()
        print(f"📬 Total unread emails: {len(unread_ids)}")

        if not unread_ids:
            print("Koi unread email nahi hai.")
            mail.logout()
            return

        # IMAP sequence numbers ascending order (purane -> naye) mein aate hain,
        # isliye list ka LAST element hi sabse latest/naya email hota hai.
        latest_id = unread_ids[-1]

        # Is baar poora email fetch karo (RFC822 = full message, header + body)
        status, data = mail.fetch(latest_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_str(msg.get("Subject"))
        from_ = decode_str(msg.get("From"))
        date_ = msg.get("Date")
        body = get_email_body(msg)

        print("\n" + "=" * 55)
        print("📨 LATEST UNREAD EMAIL")
        print("=" * 55)
        print(f"From:    {from_}")
        print(f"Subject: {subject}")
        print(f"Date:    {date_}")
        print("-" * 55)
        print("Body (pehle 500 characters):")
        print(body.strip()[:500])
        print("=" * 55)

        mail.logout()
        print("\n✅ Test complete!")

    except imaplib.IMAP4.error as e:
        print(f"❌ Login fail hua: {e}")
        print("   Check karo: App Password sahi copy kiya (bina spaces ke)?")
    except Exception as e:
        print(f"❌ Kuch error aaya: {e}")


if __name__ == "__main__":
    test_connection()
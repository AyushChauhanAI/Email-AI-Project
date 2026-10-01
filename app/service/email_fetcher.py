import imaplib
import email
from email.header import decode_header

def fetch_latest_emails(num_emails: int, username: str, app_password: str):
    """
    Gmail IMAP ka use karke specified number of latest emails fetch karta hai.
    """
    try:
        # 1. Gmail IMAP server se connect karein (SSL port 993)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        
        # 2. Login karein (Gmail App Password ka use karein)
        mail.login(username, app_password)
        
        # 3. Inbox folder select karein
        mail.select("inbox")
        
        # 4. Saari mails ki IDs search karein
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            raise Exception("Mails fetch karne mein error aayi.")
            
        email_ids = messages[0].split()
        
        # Agar mailbox khali hai
        if not email_ids:
            return []
            
        # 5. Latest mails lene ke liye IDs ko reverse karein aur 'num_emails' tak limit karein
        # (IMAP mein pehle aane wali IDs purani hoti hain, isliye end se uthayenge)
        latest_ids = email_ids[-num_emails:]
        latest_ids.reverse() # Sabse latest sabse upar rakhne ke liye
        
        fetched_emails = []
        
        for e_id in latest_ids:
            # Har email ko fetch karein (RFC822 format full raw message ke liye)
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Email parse karein
                    msg = email.message_from_bytes(response_part[1])
                    
                    # --- Subject Decode karein ---
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                        
                    # --- Sender (From) Decode karein ---
                    from_ = msg.get("From")
                    
                    headers = {
                        "Subject": subject,
                        "From": from_,
                        "To": msg.get("To"),
                        "Date": msg.get("Date")
                    }
                    
                    # --- Body Extract karein ---
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Disposition"))
                            
                            # Sirf text/plain ya text/html parts lenge
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                                except:
                                    pass
                    else:
                        # Agar mail multipart nahi hai (simple text)
                        try:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except:
                            body = str(msg.get_payload())
                            
                    fetched_emails.append({
                        "headers": headers,
                        "body": body.strip()
                    })
                    
        # Logout kardein connection band karne ke liye
        mail.logout()
        return fetched_emails

    except Exception as e:
        raise Exception(f"Gmail connection ya fetch error: {str(e)}")
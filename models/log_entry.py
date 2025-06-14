# models/log_entry.py
import re
from datetime import datetime
from utils.crypto_utils import encrypt, decrypt
from models.user import USERNAME_RE

class LogEntry:
    def __init__(self, user_id: str, username: str, description: str,
                 *, additional: str = "", suspicious: bool = False):
        
        if not USERNAME_RE.fullmatch(username):
            raise ValueError("username does not meet format/length rules")

        self.user_id = user_id
        now = datetime.now()
        self.date = now.strftime("%Y-%m-%d")
        self.time = now.strftime("%H:%M:%S")
        self.username = username.lower()
        self.description = description
        self.additional = additional
        self.suspicious = suspicious

    def as_csv(self) -> str:
        flag = "Yes" if self.suspicious else "No"
        return f"{self.date},{self.time},{self.username}," \
               f"{self.description},{self.additional},{flag}"

    def __repr__(self) -> str:
        return (
            f"LogEntry(user_id={self.user_id}, username={self.username}, "
            f"date={self.date}, time={self.time}, description={self.description}, "
            f"additional={self.additional}, suspicious={self.suspicious})"
        )
        

# This mehtod could be used when you want to add a logEntry to the log_file.txt
# def append_log(entry: LogEntry, path: str = "log_file.txt") -> None:
#     # 1. serialize
#     line = entry.as_csv()
#     # 2. encrypt full line
#     token = encrypt(line)          # => bytes
#     # 3. write token as base64 string (one line)
#     with open(path, "ab") as fh:
#         fh.write(token + b"\n")

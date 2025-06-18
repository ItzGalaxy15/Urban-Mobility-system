# models/log_entry.py
import re
from datetime import datetime
from models.user import USERNAME_RE

class LogEntry:
    def __init__(self, user_id: str, username: str, description: str,
                 *, additional: str = "", suspicious: bool = False, log_id: int = None):
        
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
        self.log_id = log_id

    def as_line(self) -> str:
        flag = "Yes" if self.suspicious else "No"
        return f"{self.log_id}|{self.date}|{self.time}|{self.username}|{self.description}|{self.additional}|{flag}"

    def __repr__(self) -> str:
        return (
            f"LogEntry("
            f"log_id={self.log_id}, user_id={self.user_id}, username={self.username}, "
            f"date={self.date}, time={self.time}, "
            f"description={self.description}, additional={self.additional}, "
            f"suspicious={self.suspicious})"
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

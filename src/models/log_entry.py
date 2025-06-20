# models/log_entry.py
import re
from datetime import datetime

class LogEntry:
    def __init__(self, user_id: str, username: str, description: str,
                 *, additional: str = "", suspicious: bool = False, log_id: int = None):

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

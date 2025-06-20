# models/log_entry.py
import re
from datetime import datetime
DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")

class LogEntry:
    def __init__(self, user_id: str, username: str, description: str,
                  additional: str = "", suspicious: bool = False, log_id: int = None, date = None, time = None):

        def is_valid_date(s: str) -> bool:
            return isinstance(s, str) and DATE_RE.fullmatch(s)

        def is_valid_time(s: str) -> bool:
            return isinstance(s, str) and TIME_RE.fullmatch(s)

        self.user_id = user_id
        now = datetime.now()
        self.date = date if is_valid_date(date) else now.strftime("%Y-%m-%d")
        self.time = time if is_valid_time(time) else now.strftime("%H:%M:%S")
        self.username = username.lower()
        self.description = description
        self.additional = additional
        self.suspicious = suspicious
        self.log_id = log_id

    def as_line(self) -> str:
        flag = "Yes" if self.suspicious else "No"
        return f"{self.log_id}|{self.date}|{self.time}|{self.username}|{self.description}|{self.additional}|{flag}|{self.user_id}"
    

    def __repr__(self) -> str:
        return (
            f"LogEntry("
            f"log_id={self.log_id}, user_id={self.user_id}, username={self.username}, "
            f"date={self.date}, time={self.time}, "
            f"description={self.description}, additional={self.additional}, "
            f"suspicious={self.suspicious})"
        )

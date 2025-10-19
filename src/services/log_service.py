# services/log_service.py
import os
from models.log_entry import LogEntry
from utils.crypto_utils import decrypt, encrypt
from collections import defaultdict
from models.log_entry import LogEntry
import sqlite3
from pathlib import Path
from config import DB_FILE, LOG_FILE

_failed_counter = defaultdict(int)   # username -> consecutive fails

def get_next_log_id() -> int:
    """
    Determine the next incremental log_id.

    Counts how many lines (encrypted log records) are already present
    in the log file. If the file does not exist, the first log_id is 1.
    """
    if not os.path.exists(LOG_FILE):
        return 1
    # Each line is one log entry -> line count == last id
    with open(LOG_FILE, "rb") as f:
        return sum(1 for _ in f) + 1


def write_log_entry(entry: LogEntry) -> None:
    """
    Encrypts a LogEntry and appends it to the log file.

    Args:
        entry (LogEntry): fully populated log entry (log_id is set here).
    """
    entry.log_id = get_next_log_id()
    line = entry.as_line()          # Plain text (pipe-separated) line
    token = encrypt(line)           # => bytes
    with open(LOG_FILE, "ab") as f:
        f.write(token + b"\n")      # One encrypted line per entry

def log_login_attempt(username: str, success: bool):
    if success:
        _failed_counter.clear()          # reset ALL counters on first success
    else:
        _failed_counter[username] += 1

    total_fails = sum(_failed_counter.values())
    suspicious  = total_fails >= 3       # 3 consecutive fails (any usernames)

    # Dynamic description
    if success:
        desc = "Successful login"
    elif suspicious:
        desc = "Multiple usernames/passwords tried in a row"
    else:
        desc = "Unsuccessful login"

    write_log_entry(LogEntry(
        user_id="-",
        username=username,
        description=desc,
        additional=f"fail_count={total_fails}",
        suspicious=suspicious
    ))


def read_logs(limit: int | None = None) -> list[LogEntry]:
    """
    Decrypts log file and returns LogEntry objects (newest first).
    limit – show only the latest N entries if provided.
    """
    if not os.path.exists(LOG_FILE):
        return []

    entries: list[LogEntry] = []
    with open(LOG_FILE, "rb") as f:
        for token in f:
            try:
                line = decrypt(token.strip())  # "log_id|date|time|username|description|additional|flag|user_id"
                parts = line.split("|")
                entry = LogEntry(
                    user_id=parts[7],
                    username=parts[3],
                    description=parts[4],
                    additional=parts[5],
                    suspicious=(parts[6] == "Yes"),
                    log_id=int(parts[0]),
                    date=parts[1],
                    time=parts[2]
                )
                entries.append(entry)
            except Exception:
                # corrupted line? skip
                continue

    entries.reverse()          # newest first
    if limit:
        entries = entries[:limit]
    return entries


def _conn():
    return sqlite3.connect(DB_FILE)

def unread_suspicious_count(user_id: int) -> int:
    """
    Returns how many suspicious logs have appeared
    since this admin's last_seen_log_id.
    """
    last_seen = 0
    with _conn() as conn:
        c = conn.cursor()
        c.execute('SELECT last_seen_log_id FROM LogStatus WHERE user_id=?', (user_id,))
        row = c.fetchone()
        if row:
            last_seen = row[0]

    # read newest logs
    logs = read_logs()               # already returns newest→oldest
    unseen = [e for e in logs if e.suspicious and e.log_id > last_seen]
    return len(unseen)

def mark_logs_read(user_id: int) -> None:
    """Store highest log_id as last seen for this admin."""
    logs = read_logs(limit=1)        # latest only
    if not logs:
        return
    top_id = logs[0].log_id
    with _conn() as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO LogStatus (user_id,last_seen_log_id) VALUES (?,?)',
                  (user_id, top_id))
        conn.commit()
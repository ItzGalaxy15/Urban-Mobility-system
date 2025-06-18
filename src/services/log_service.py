# services/log_service.py
import os
from models.log_entry import LogEntry
from utils.crypto_utils import decrypt, encrypt
from collections import defaultdict
from models.log_entry import LogEntry

LOG_FILE = "activity.log"
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
    # token = encrypt(line)           # => bytes
    # with open(LOG_FILE, "ab") as f:
    #     f.write(token + b"\n")      # One encrypted line per entry

    line = entry.as_line()
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

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
    # this should activated before we deliver it
    # with open(LOG_FILE, "rb") as f:
    #     for token in f:
    #         try:
    #             line = decrypt(token.strip())          # "id|date|time|..."
    #             parts = line.split("|")
    #             entry = LogEntry(
    #                 user_id=parts[1],                  # we ignore stored id order
    #                 username=parts[3],
    #                 description=parts[4],
    #                 additional=parts[5],
    #                 suspicious=(parts[6] == "Yes"),
    #                 log_id=int(parts[0])
    #             )
    #             entries.append(entry)
    #         except Exception:
    #             # corrupted line? skip
    #             continue

    # entries.reverse()          # newest first
    # if limit:
    #     entries = entries[:limit]
    # return entries

    # Temporarily so I can see the log file with normal characters
    with open(LOG_FILE, "r") as f:  # Open in text mode, not binary
        for line in f:
            try:
                line = line.strip()  # Remove any surrounding whitespace or newline
                parts = line.split("|")
                entry = LogEntry(
                    user_id=parts[1],                  # we ignore stored id order
                    username=parts[3],
                    description=parts[4],
                    additional=parts[5],
                    suspicious=(parts[6] == "Yes"),
                    log_id=int(parts[0])
                )
                entries.append(entry)
            except Exception:
                # corrupted line? skip
                continue

    entries.reverse()          # newest first
    if limit:
        entries = entries[:limit]
    return entries


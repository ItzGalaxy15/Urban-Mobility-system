# services/log_service.py
import os
from models.log_entry import LogEntry
from utils.crypto_utils import encrypt
from collections import defaultdict

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


# def log_login_attempt(username: str, success: bool):
#     """
#     Track consecutive failures per username and log the attempt.
#     After 3 fails in a row, mark it suspicious=True.
#     """
#     if success:
#         _failed_counter[username] = 0          # reset on success
#     else:
#         _failed_counter[username] += 1

#     suspicious = _failed_counter[username] >= 3

#     write_log_entry(LogEntry(
#         user_id="-",                      # unknown before auth
#         username=username,
#         description="Successful login" if success else "Unsuccessful login",
#         additional=f"fail_count={_failed_counter[username]}",
#         suspicious=suspicious
#     ))
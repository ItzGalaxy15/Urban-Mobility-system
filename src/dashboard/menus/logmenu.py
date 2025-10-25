# dashboard/menus/logmenu.py
from services.log_service import read_logs
from services.session_service import session_service
from services.log_service import mark_logs_read

def view_logs_flow(session):
    print("\n=== System Logs (latest 100) ===")
    logs = read_logs(limit=100)

    if not logs:
        print("No log entries yet.")
    else:
        print("ID  | Date       | Time     | Username     |  ⚠  |   additional  | Description")
        print("-" * 90)
        for e in logs:
            flag = "⚠" if e.suspicious else " "
            print(f"{e.log_id:>3} | {e.date} | {e.time} | {e.username:<12} |  {flag:<1}  | {e.additional:<13} | {e.description}")

    if session_service.get_current_role() in ("system_admin", "super"):
        mark_logs_read(session_service.get_current_user_id())

    input("\nPress Enter to continue...")
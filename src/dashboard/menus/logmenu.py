# dashboard/menus/logmenu.py
from services.log_service import read_logs
from controllers.session import UserSession

def view_logs_flow(session):
    print("\n=== System Logs (latest 100) ===")
    logs = read_logs(limit=100)

    if not logs:
        print("No log entries yet.")
    else:
        print("ID  | Date       | Time     | Username     |  ⚠  | Description")
        print("-" * 72)
        for e in logs:
            flag = "⚠" if e.suspicious else " "
            print(f"{e.log_id:>3} | {e.date} | {e.time} | {e.username:<12} |  {flag:<1}  | {e.description}")


    input("\nPress Enter to continue...")

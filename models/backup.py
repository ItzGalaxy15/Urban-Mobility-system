# models/backup.py
from datetime import datetime
from utils.crypto_utils import encrypt, decrypt

class Backup:
    """
    Represents a backup metadata record.
    All attributes are encrypted except the object’s own reference;
    this keeps file‐system details and user IDs private.
    """

    def __init__(self, file_path: str, created_by_user_id: int):
        # Encrypt every field we store
        self.file_path          = encrypt(file_path)
        self.created_by_user_id = encrypt(str(created_by_user_id))
        self.backup_date        = encrypt(datetime.now().isoformat())

    # Getters
    @property
    def file_path_plain(self) -> str:
        return decrypt(self.file_path)

    @property
    def created_by_user_id_plain(self) -> int:
        return int(decrypt(self.created_by_user_id))

    @property
    def backup_date_plain(self) -> datetime:
        return datetime.fromisoformat(decrypt(self.backup_date))


    def __repr__(self) -> str:
        return (
            f"<Backup path={self.file_path_plain} "
            f"created_by={self.created_by_user_id_plain} "
            f"created_at={self.backup_date_plain.isoformat()}>"
        )
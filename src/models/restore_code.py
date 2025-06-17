# models/restore_code.py
from datetime import datetime
from utils.crypto_utils import encrypt, decrypt, hash_password, check_password

class RestoreCode:
    def __init__(self, plain_code: str, backup_id: int, admin_user_id: int):
        # store code hash
        self.code_hash              = hash_password(plain_code)

        # rest encrypt
        self.backup_id              = encrypt(str(backup_id))
        self.system_admin_user_id   = encrypt(str(admin_user_id))
        self.generated_date         = encrypt(datetime.now().isoformat())
        self.is_used                = encrypt("0")          # “0” = False

    # -------- helpers --------
    def verify(self, typed_code: str) -> bool:
        """Check if code is correct and has not yet been used."""
        if decrypt(self.is_used) == "1":
            return False
        ok = check_password(typed_code, self.code_hash)
        if ok:
            self.is_used = encrypt("1") # mark as used
        return ok

    # Getters
    @property
    def backup_id_plain(self) -> int:
        return int(decrypt(self.backup_id))

    @property
    def system_admin_user_id_plain(self):
        return int(decrypt(self.system_admin_user_id))

    @property
    def generated_date_plain(self):
        return datetime.fromisoformat(decrypt(self.generated_date))
    
    @property
    def is_used_plain(self):
         return decrypt(self.is_used) == "1"

    def __repr__(self):
        used = self.is_used_plain == "1"
        return f"<RestoreCode backup={self.backup_id_plain} used={used}>"

from .auth import LockanaAuth
from .secrets import LockanaSecrets
from .admin import LockanaAdmin

class LockanaClient(LockanaAuth, LockanaSecrets, LockanaAdmin):
    token: str | None
    
    def __init__(self, username: str, host_url: str) -> None:
        super().__init__(username, host_url)
        self.token = None
    
    def auth_login(self, totp: str) -> str:
        """Authenticate the user and set the token for LockanaSecrets."""
        self.token = super().auth_login(totp)
        return self.token

    def auth_logout(self) -> None:
        """Logout and clear the token."""
        super().auth_logout()
        self.token = None 
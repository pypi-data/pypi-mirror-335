import requests


class LockanaAuth:
    def __init__(self, username: str, host_url: str) -> None:
        self.username = username
        self.host_url = host_url
        self.token: str | None = None

    def auth_login(self, totp: str) -> str:
        """
        Authenticate the user with the given TOTP token.

        Args:
            totp (str): The TOTP token for authentication.

        Returns:
            str: The authentication token.
        """
        response = requests.post(
            f"{self.host_url}/auth/login",
            json={"username": self.username, "totp_code": totp},
        )
        if response.status_code == 401:
            raise ValueError("Invalid auth data.")
        elif response.status_code == 500:
            raise RuntimeError("Server error.")    
        else:
            return response.json()["access_token"]
        
    def auth_logout(self) -> None:
        """
        Log out the user by invalidating the given token.

        Args:
            token (str): The authentication token to be invalidated.
        """
        
        if self.token is None:
            raise ValueError("No token provided.")
        
        response = requests.post(
            f"{self.host_url}/auth/logout",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if response.status_code == 401:
            raise ValueError("Invalid auth data.")
        elif response.status_code == 500:
            raise RuntimeError("Server error.")
        


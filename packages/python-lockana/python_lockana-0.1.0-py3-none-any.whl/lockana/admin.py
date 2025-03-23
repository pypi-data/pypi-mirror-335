import requests
from .logs import LockanaLogs


class LockanaAdmin(LockanaLogs):
    def __init__(self, base_url: str, token: str):
        super().__init__(base_url, token)
    
    def create_user(self, username: str) -> dict:
        """Создает нового пользователя."""
        url = f"{self.base_url}/admin/users/create"
        payload = {"username": username}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def delete_user(self, username: str) -> dict:
        """Удаляет пользователя по имени."""
        url = f"{self.base_url}/admin/users/delete"
        payload = {"username": username}
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.delete(url, json=payload, headers=headers)
        return response.json()
    
    def list_users(self) -> dict:
        """Получает список всех пользователей."""
        url = f"{self.base_url}/admin/users/list"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.get(url, headers=headers)
        return response.json()

import requests


class LockanaLogs:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def get_logs_file(self) -> requests.Response:
        """Получает файл логов."""
        url = f"{self.base_url}/logs/logs-file"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        return response
    
    def get_logs(self) -> requests.Response:
        """Получает список логов из базы данных."""
        url = f"{self.base_url}/logs"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.token}"})
        return response
    
    def delete_logs_file(self) -> requests.Response:
        """Удаляет файл логов."""
        url = f"{self.base_url}/logs/logs-file"
        response = requests.delete(url, headers={"Authorization": f"Bearer {self.token}"})
        return response
    
    def delete_logs(self) -> requests.Response:
        """Удаляет все логи из базы данных."""
        url = f"{self.base_url}/logs"
        response = requests.delete(url, headers={"Authorization": f"Bearer {self.token}"})
        return response

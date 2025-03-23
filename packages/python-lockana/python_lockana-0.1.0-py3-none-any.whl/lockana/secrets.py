import json
import requests


class LockanaSecrets:
    def __init__(self, host_url: str) -> None:
        self.host_url = host_url
        self.token: str | None = None

    def secrets_list(self) -> list[str]:
        if self.token is None:
            raise ValueError("No token provided.")
        
        response = requests.get(
            f"{self.host_url}/secrets/list",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to list secrets: {response.text}")
        return json.loads(response.text)["secrets"]
    
    def secrets_get(self, secret_name: str) -> str:
        if self.token is None:
            raise ValueError("No token provided.")

        response = requests.post(
            f"{self.host_url}/secrets/get",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"name": secret_name},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get secret: {response.text}")
        return json.loads(response.text)["secret"]
    
    def secrets_add(self, secret_name: str, secret_value: str) -> None:
        if self.token is None:
            raise ValueError("No token provided.")

        response = requests.post(
            f"{self.host_url}/secrets/add",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"name": secret_name, "encrypted_data": secret_value},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to add secret: {response.text}")
    
    def secrets_update(self, secret_name: str, secret_value: str) -> None:
        if self.token is None:
            raise ValueError("No token provided.")
        
        response = requests.put(
            f"{self.host_url}/secrets/update",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"name": secret_name, "encrypted_data": secret_value},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to update secret: {response.text}")
    
    def secrets_delete(self, secret_name: str) -> None:
        if self.token is None:
            raise ValueError("No token provided.")

        response = requests.delete(
            f"{self.host_url}/secrets/delete",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"name": secret_name},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to delete secret: {response.text}")
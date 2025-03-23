from lockana.client import LockanaClient

if __name__ == "__main__":
    client = LockanaClient("PYTHON_TEST", "http://localhost:8000")
    
    totp_code = input("TOTP: ")
    client.auth_login(totp_code)
    
    print("Adding a new secret...")
    client.secrets_add("TEST_SECRET", "TEST_SECRET_VALUE")
    
    print("Listing all secrets...")
    secrets = client.secrets_list()
    print(secrets)
    
    print("Deleting the secret...")
    client.secrets_delete("TEST_SECRET")
    
    print("Listing all secrets again...")
    secrets = client.secrets_list()
    print(secrets)
    
    print("Logging out...")
    client.auth_logout()

    print("Client operations completed.")

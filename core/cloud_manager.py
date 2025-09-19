import requests
import os

class CloudManager:
    """
    Gerencia integração com API do Render (status, restart, deploy).
    """
    def __init__(self, service_id=None, api_key=None):
        self.api_key = api_key or os.getenv('RENDER_API_KEY')
        self.service_id = service_id or os.getenv('RENDER_SERVICE_ID')
        self.base_url = 'https://api.render.com/v1/services'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def get_status(self):
        url = f"{self.base_url}/{self.service_id}"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        print(f"Erro ao consultar status: {resp.text}")
        return None

    def restart_service(self):
        url = f"{self.base_url}/{self.service_id}/restart"
        resp = requests.post(url, headers=self.headers)
        if resp.status_code == 200:
            print("Serviço reiniciado com sucesso.")
            return True
        print(f"Erro ao reiniciar serviço: {resp.text}")
        return False

    def deploy_new_instance(self, image_url):
        url = f"{self.base_url}/{self.service_id}/deploy"
        data = {"image": image_url}
        resp = requests.post(url, headers=self.headers, json=data)
        if resp.status_code == 200:
            print("Nova instância criada com sucesso.")
            return True
        print(f"Erro ao criar instância: {resp.text}")
        return False

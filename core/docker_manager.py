import subprocess
import os

class DockerManager:
    """
    Gerencia operações Docker: build, push e deploy automáticos.
    """
    def __init__(self, image_name, dockerfile_path='Dockerfile', registry_url=None):
        self.image_name = image_name
        self.dockerfile_path = dockerfile_path
        self.registry_url = registry_url or os.getenv('DOCKER_REGISTRY_URL')

    def build_image(self, tag='latest'):
        full_image = f"{self.image_name}:{tag}"
        print(f"🔨 Buildando imagem Docker: {full_image}")
        cmd = ["docker", "build", "-t", full_image, "-f", self.dockerfile_path, "."]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Erro ao buildar imagem: {result.stderr}")
            return False
        return True

    def push_image(self, tag='latest'):
        full_image = f"{self.image_name}:{tag}"
        if self.registry_url:
            full_image = f"{self.registry_url}/{full_image}"
        print(f"🚀 Enviando imagem para o registry: {full_image}")
        cmd = ["docker", "push", full_image]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Erro ao enviar imagem: {result.stderr}")
            return False
        return True

    def deploy_container(self, tag='latest', detach=True):
        full_image = f"{self.image_name}:{tag}"
        print(f"⚡ Iniciando container: {full_image}")
        cmd = ["docker", "run"]
        if detach:
            cmd.append("-d")
        cmd.append(full_image)
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Erro ao iniciar container: {result.stderr}")
            return False
        return True

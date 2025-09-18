import os
import subprocess

# Cores para o output
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Função para executar comandos no shell
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{bcolors.FAIL}Erro ao executar o comando: {command}{bcolors.ENDC}")
        print(e)
        exit(1)

# 1. Verificar se o token do Telegram está configurado
print(f"{bcolors.HEADER}Verificando o token do Telegram...{bcolors.ENDC}")
if 'TELEGRAM_BOT_TOKEN' in os.environ:
    print(f"{bcolors.OKGREEN}Token do Telegram encontrado!{bcolors.ENDC}")
else:
    print(f"{bcolors.WARNING}Token do Telegram não encontrado. Por favor, configure a variável de ambiente TELEGRAM_BOT_TOKEN.{bcolors.ENDC}")

# 2. Instalar dependências
print(f"{bcolors.HEADER}Instalando dependências...{bcolors.ENDC}")
run_command("pip install -r requirements.txt")

# 3. Executar o bot do Telegram
print(f"{bcolors.HEADER}Iniciando o bot do Telegram...{bcolors.ENDC}")
run_command("python run_integrated_system.py")


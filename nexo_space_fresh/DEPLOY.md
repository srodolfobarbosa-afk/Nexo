# 🚀 Guia de Deploy - NEXO V37.3

## Deploy no Hugging Face Spaces

### Passo 1: Criar um Space

1. Acesse [Hugging Face Spaces](https://huggingface.co/spaces)
2. Clique em **"Create new Space"**
3. Preencha as informações:
   - **Owner**: NEXO-MAESTRO (ou seu usuário)
   - **Space name**: srodolfobarbosa
   - **License**: MIT
   - **Select the Space SDK**: **Docker**
   - **Space hardware**: CPU basic (gratuito) ou GPU para melhor performance

### Passo 2: Configurar Secrets

No seu Space, vá em **Settings** → **Repository secrets** e adicione:

```
GROQ_API_KEY = gsk_your_actual_key_here
```

Opcionalmente, adicione também:
```
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your_supabase_key_here
```

### Passo 3: Fazer Upload dos Arquivos

Você pode fazer upload via interface web ou Git:

#### Opção A: Interface Web
1. Clique em **Files** → **Add file**
2. Faça upload dos seguintes arquivos:
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `README.md`

#### Opção B: Via Git
```bash
# Clone o repositório do Space
git clone https://huggingface.co/spaces/NEXO-MAESTRO/srodolfobarbosa
cd srodolfobarbosa

# Adicione os arquivos
cp /caminho/para/nexo_project/* .

# Commit e push
git add .
git commit -m "Deploy NEXO V37.3"
git push
```

### Passo 4: Aguardar Build

O Hugging Face irá:
1. Construir a imagem Docker
2. Instalar dependências
3. Iniciar o servidor
4. Seu Space estará disponível em: `https://huggingface.co/spaces/NEXO-MAESTRO/srodolfobarbosa`

## Deploy Local com Docker

### Construir Imagem

```bash
docker build -t nexo-maestro:37.3 .
```

### Executar Container

```bash
docker run -d \
  --name nexo-maestro \
  -p 7860:7860 \
  -e GROQ_API_KEY="gsk_your_key" \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SUPABASE_KEY="your_key" \
  -v $(pwd)/data:/data \
  nexo-maestro:37.3
```

### Verificar Logs

```bash
docker logs -f nexo-maestro
```

### Acessar

Abra no navegador: `http://localhost:7860`

## Deploy em Servidor VPS

### Requisitos
- Ubuntu 20.04+ ou Debian 11+
- Python 3.11+
- 2GB RAM mínimo
- 10GB disco

### Instalação

```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Python e dependências
sudo apt-get install -y python3.11 python3-pip git

# Instalar Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Clonar projeto
git clone https://huggingface.co/spaces/NEXO-MAESTRO/srodolfobarbosa
cd srodolfobarbosa

# Configurar ambiente
cp .env.example .env
nano .env  # Edite e adicione suas chaves

# Instalar dependências
pip3 install -r requirements.txt

# Executar
python3 app.py
```

### Executar como Serviço (systemd)

Crie `/etc/systemd/system/nexo-maestro.service`:

```ini
[Unit]
Description=NEXO MAESTRO V37.3
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/srodolfobarbosa
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexo-maestro
sudo systemctl start nexo-maestro
sudo systemctl status nexo-maestro
```

## Configuração de Proxy Reverso (Nginx)

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Erro: Chrome não encontrado
```bash
# Instalar Chrome
sudo apt-get install -y google-chrome-stable

# Ou Chromium
sudo apt-get install -y chromium-browser
```

### Erro: Porta 7860 em uso
```bash
# Verificar processo
sudo lsof -i :7860

# Matar processo
sudo kill -9 <PID>

# Ou usar outra porta
export PORT=8080
python3 app.py
```

### Erro: Memória insuficiente
```bash
# Adicionar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Logs não aparecem
```bash
# Executar com logs detalhados
python3 app.py --log-level debug
```

## Monitoramento

### Verificar Status
```bash
curl http://localhost:7860/health
```

### Ver Logs em Tempo Real
```bash
tail -f logs/nexo.log
```

### Métricas do Sistema
```bash
curl http://localhost:7860/status
```

## Backup e Restauração

### Backup
```bash
# Backup de habilidades
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup do banco (se usar Supabase)
# Use o dashboard do Supabase para exportar
```

### Restauração
```bash
# Restaurar habilidades
tar -xzf backup-20260110.tar.gz
```

## Atualizações

### Atualizar Código
```bash
cd srodolfobarbosa
git pull
pip3 install -r requirements.txt --upgrade
sudo systemctl restart nexo-maestro
```

## Segurança

### Firewall
```bash
# Permitir apenas porta 7860
sudo ufw allow 7860/tcp
sudo ufw enable
```

### HTTPS com Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## Suporte

- **Issues**: https://huggingface.co/spaces/NEXO-MAESTRO/srodolfobarbosa/discussions
- **Documentação**: README.md
- **Exemplos**: Ver pasta `examples/` (se disponível)

---

**🔱 NEXO V37.3 - Deploy com Sucesso!**

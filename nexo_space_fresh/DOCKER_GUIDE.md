# 🐳 NEXO v2026 - Guia Docker Completo

## Opção 1: Docker Compose (RECOMENDADO)

### Preparação

```bash
# 1. Clone ou acesse o repositório
cd /workspaces/rodolfo

# 2. Copie o arquivo de configuração
cp .env.docker.example .env

# 3. Edite .env com suas chaves
nano .env  # ou use seu editor preferido
```

### Iniciar

```bash
# Iniciar o container
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Acessar em: http://localhost:7860
```

### Parar

```bash
docker-compose down
```

---

## Opção 2: Docker Run (Manual)

```bash
docker run -it -p 7860:7860 --platform=linux/amd64 \
  -e PINECONE_API_KEY="YOUR_VALUE_HERE" \
  -e GROQ_API_KEY="YOUR_VALUE_HERE" \
  -e HF_TOKEN="YOUR_VALUE_HERE" \
  -e SUPABASE_URL="YOUR_VALUE_HERE" \
  -e SUPABASE_KEY="YOUR_VALUE_HERE" \
  -e GROQ_KEY_1="YOUR_VALUE_HERE" \
  -e GROQ_KEY_2="YOUR_VALUE_HERE" \
  -e GROQ_KEY_3="YOUR_VALUE_HERE" \
  -e GROQ_KEY_4="YOUR_VALUE_HERE" \
  -e GROQ_KEY_5="YOUR_VALUE_HERE" \
  registry.hf.space/nexo-maestro-srodolfobarbosa:latest
```

---

## Opção 3: Script de Deploy

```bash
# Dar permissão de execução
chmod +x docker-deploy.sh

# Usar o script
./docker-deploy.sh start      # Inicia
./docker-deploy.sh stop       # Para
./docker-deploy.sh rebuild    # Reconstrói
./docker-deploy.sh logs       # Logs
./docker-deploy.sh shell      # Shell no container
./docker-deploy.sh push       # Push para HF Registry
```

---

## 📋 Variáveis de Ambiente Necessárias

### Essenciais (Mínimo para funcionar)

```env
GROQ_API_KEY=gsk_...
HF_TOKEN=hf_...
```

### Recomendadas

```env
PINECONE_API_KEY=pcsk_...
SUPABASE_URL=https://...
SUPABASE_KEY=sb_...
```

### Rodízio de Chaves (Resiliência)

```env
GROQ_KEY_1=gsk_...
GROQ_KEY_2=gsk_...
GROQ_KEY_3=gsk_...
GROQ_KEY_4=gsk_...
GROQ_KEY_5=gsk_...
```

---

## 🔍 Verificar Status

```bash
# Ver containers rodando
docker ps

# Ver logs
docker logs nexo-v2026

# Entrar no container
docker exec -it nexo-v2026 bash

# Ver recursos utilizados
docker stats nexo-v2026
```

---

## 🚀 Deploy em Produção

### HF Spaces (Container Registry)

```bash
# 1. Build da imagem
docker build -t registry.hf.space/nexo-maestro-srodolfobarbosa:latest .

# 2. Push para HF Registry
docker push registry.hf.space/nexo-maestro-srodolfobarbosa:latest

# 3. O HF Spaces detectará automaticamente
```

### AWS/Google Cloud/Azure

```bash
# Adapte os comandos para seu provedor
docker build -t seu-registry/nexo-v2026:latest .
docker push seu-registry/nexo-v2026:latest
```

---

## 📊 Performance

### Requisitos Mínimos

- CPU: 2 cores
- RAM: 2 GB
- Disco: 5 GB

### Requisitos Recomendados

- CPU: 4+ cores
- RAM: 8 GB
- Disco: 10 GB
- GPU: Opcional (para IA mais rápida)

---

## 🐛 Troubleshooting

### Port já em uso

```bash
# Mudar porta no docker-compose.yml
ports:
  - "8000:7860"  # Host:Container
```

### Sem permissão

```bash
chmod +x docker-deploy.sh
docker ps  # Testar permissões
```

### Build falha

```bash
docker-compose build --no-cache
```

### Container não inicia

```bash
docker logs nexo-v2026
```

---

## 📝 Exemplo Completo

```bash
# 1. Preparar
cp .env.docker.example .env
# Editar .env com suas chaves

# 2. Build
docker-compose build

# 3. Iniciar
docker-compose up -d

# 4. Verificar
docker-compose logs -f

# 5. Acessar
# Abra: http://localhost:7860

# 6. Parar (quando necessário)
docker-compose down
```

---

## 🔐 Segurança

✅ **Sempre faça:**
- Use `.env` para variáveis sensíveis
- Não versione `.env` (está no `.gitignore`)
- Use HTTPS em produção
- Regenere tokens regularmente

❌ **Nunca faça:**
- Coloque credenciais no Dockerfile
- Compartilhe `.env`
- Use credenciais antigas

---

## 📞 Suporte

Documentação completa: [GUIA_USO_v2026.md](GUIA_USO_v2026.md)

Status: Pronto para produção 🚀

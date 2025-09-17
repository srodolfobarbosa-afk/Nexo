# Configuração do Bot do Telegram - Nexo

## 📋 Pré-requisitos

1. **Token do Bot do Telegram**
   - Acesse o [@BotFather](https://t.me/botfather) no Telegram
   - Use o comando `/newbot` para criar um novo bot
   - Siga as instruções para definir nome e username
   - Copie o token fornecido pelo BotFather

## ⚙️ Configuração no Render

### 1. Adicionar Variável de Ambiente

No dashboard do Render, adicione a seguinte variável de ambiente:

```
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

### 2. Verificar Outras Variáveis

Certifique-se de que estas variáveis estão configuradas:
- `OPENAI_API_KEY`
- `GEMINI_API_KEY` 
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `NEXO_URL` (opcional, padrão: https://nexo-kh57.onrender.com)

## 🚀 Execução

### Opção 1: Executar Localmente (para testes)

```bash
cd /home/ubuntu/Nexo
python run_telegram_bot.py
```

### Opção 2: Deploy no Render

O bot pode ser executado como um serviço separado no Render:

1. Crie um novo Web Service no Render
2. Conecte ao mesmo repositório GitHub
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python run_telegram_bot.py`
   - **Environment:** Python 3

## 🤖 Comandos do Bot

### Comandos Básicos
- `/start` - Iniciar o bot e ver boas-vindas
- `/help` - Mostrar ajuda e comandos disponíveis
- `/status` - Verificar status do sistema Nexo
- `/context` - Ver histórico da conversa
- `/clear` - Limpar contexto da conversa

### Uso Geral
- Envie qualquer mensagem e o bot processará através do sistema Nexo
- O bot mantém contexto das conversas
- Respostas são processadas de forma autônoma

## 🔧 Funcionalidades

### Integração com Nexo
- **Processamento de IA:** Mensagens são processadas pelo sistema Nexo
- **Contexto Persistente:** Mantém histórico das conversas
- **Operação Autônoma:** Funciona independentemente da interface web
- **API Integrada:** Comunicação direta com endpoints do Nexo

### Capacidades
- ✅ Análise e pesquisa de informações
- ✅ Criação de conteúdo e documentos
- ✅ Automação de tarefas repetitivas
- ✅ Gerenciamento de projetos
- ✅ Integração com APIs externas

## 🛡️ Segurança

### Autorização
- Por padrão, todos os usuários têm acesso
- Para restringir acesso, modifique a função `is_authorized()` em `telegram_bot.py`
- Implemente lista de usuários autorizados usando Supabase

### Logs
- Todas as interações são logadas
- Erros são capturados e reportados
- Contexto das conversas é mantido em memória

## 🔄 Monitoramento

### Health Check
- Endpoint: `GET /health`
- Verifica conectividade com o Nexo
- Retorna status do sistema

### Status da API
- Endpoint: `GET /api/status`
- Informações detalhadas do sistema
- Lista de capacidades disponíveis

## 🐛 Troubleshooting

### Bot não responde
1. Verifique se `TELEGRAM_BOT_TOKEN` está configurado
2. Confirme se o serviço Nexo está online
3. Verifique logs do Render para erros

### Erro de conexão com Nexo
1. Verifique se `NEXO_URL` está correto
2. Teste endpoint `/health` manualmente
3. Confirme se todas as dependências estão instaladas

### Problemas de dependências
```bash
pip install -r requirements.txt
```

## 📈 Próximos Passos

1. **Implementar autenticação** com lista de usuários autorizados
2. **Adicionar comandos específicos** para funcionalidades do Nexo
3. **Integrar com Supabase** para persistência de contexto
4. **Implementar webhooks** para melhor performance
5. **Adicionar métricas** e analytics de uso

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs no Render
2. Teste endpoints da API manualmente
3. Confirme configuração das variáveis de ambiente
4. Verifique conectividade entre serviços

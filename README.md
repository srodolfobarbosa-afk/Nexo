# 🌱 EcoGuardians - Sistema Autônomo de IA

## Visão Geral

O **EcoGuardians** é um ecossistema de agentes de inteligência artificial autônomos e auto-construtores, projetado para interpretar missões em linguagem natural e criar automaticamente novos agentes especializados para executá-las.

## 🚀 Características Principais

- **Nexo Gênesis**: Agente orquestrador principal que interpreta missões e cria novos agentes
- **Auto-Construção**: Capacidade de gerar código e criar novos agentes automaticamente
- **Interface de Chat**: Interface web moderna para interação em linguagem natural
- **Multi-LLM**: Suporte para Google Gemini, OpenAI GPT e Groq
- **Banco de Dados**: Integração com Supabase para persistência de dados
- **Deploy Automático**: Pronto para deploy no Render

## 🛠️ Tecnologias

- **Backend**: Python, Flask, Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Banco de Dados**: Supabase (PostgreSQL)
- **IA/LLM**: Google Gemini, OpenAI, Groq
- **Deploy**: Render, GitHub

## 📦 Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/srodolfobarbosa-afk/Nexo.git
cd Nexo
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente no arquivo `.env`:
```env
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
GEMINI_API_KEY=sua_chave_do_gemini
OPENAI_API_KEY=sua_chave_do_openai
GROQ_API_KEY=sua_chave_do_groq
NEXO_LLM_PROVIDER=google
```

4. Execute a aplicação:
```bash
python nexo.py
```

5. Acesse: `http://localhost:5000`

## 🌐 Deploy no Render

1. Conecte seu repositório GitHub ao Render
2. Configure as variáveis de ambiente no painel do Render
3. O deploy será automático usando o arquivo `render.yaml`

### Variáveis de Ambiente Necessárias no Render:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `NEXO_LLM_PROVIDER` (padrão: google)

## 🤖 Como Usar

1. **Acesse a Interface**: Abra a aplicação no navegador
2. **Digite uma Missão**: Exemplo: "Crie um agente para monitorar o mercado de criptomoedas"
3. **Aguarde o Processamento**: O Nexo Gênesis interpretará e criará o agente automaticamente
4. **Acompanhe o Progresso**: Veja o status em tempo real na interface

## 📁 Estrutura do Projeto

```
Nexo/
├── agentes/                 # Agentes especializados
│   ├── __init__.py
│   ├── EcoFinance.py       # Agente de finanças
│   └── NexoGenesis.py      # Agente orquestrador
├── core/                   # Módulos centrais
│   ├── __init__.py
│   └── database.py         # Conexão com Supabase
├── static/                 # Interface web
│   └── index.html          # Interface de chat
├── .env                    # Variáveis de ambiente
├── nexo.py                 # Aplicação principal Flask
├── requirements.txt        # Dependências Python
├── render.yaml            # Configuração do Render
└── README.md              # Este arquivo
```

## 🧪 Testes

Execute os testes:
```bash
pytest test_nexo.py
```

## 🎯 Exemplos de Missões

- "Crie um agente para monitorar preços de ações"
- "Desenvolva um bot para análise de sentimento em redes sociais"
- "Implemente um sistema de alertas para oportunidades de investimento"
- "Crie um agente para automatizar relatórios financeiros"

## 🔧 Desenvolvimento

### Adicionando Novos Agentes

Os agentes são criados automaticamente pelo Nexo Gênesis, mas você também pode criar manualmente:

1. Crie um arquivo em `agentes/NomeDoAgente.py`
2. Implemente a classe seguindo o padrão dos agentes existentes
3. Conecte-se ao Supabase usando `core.database`

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Suporte

Para suporte e dúvidas, abra uma issue no GitHub ou entre em contato através dos canais oficiais.

---

**Desenvolvido com ❤️ para automatizar e facilitar a criação de agentes de IA**

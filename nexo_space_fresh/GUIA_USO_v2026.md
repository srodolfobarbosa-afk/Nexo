# 🚀 COMO USAR O MOTOR DE DECISÃO NEXO v2026

## Arquitetura Implementada

O **BotEngenheiroNexo** implementa um Motor de Decisão com 3 fases:

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  1. PLANEJAR     │ ───> │   2. AGIR        │ ───> │  3. OBSERVAR     │
├──────────────────┤      ├──────────────────┤      ├──────────────────┤
│ Define passos    │      │ Executa          │      │ Analisa          │
│ Cria estratégia  │      │ Ferramentas      │      │ resultados       │
│ Planejamento     │      │ Acumula contexto │      │ Aprende          │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

---

## 📝 Exemplo de Uso

### Inicializar o Bot:

```python
from bot_engenheiro_v2 import BotEngenheiroNexo
import asyncio

async def main():
    # Criar instância
    bot = BotEngenheiroNexo()
    
    # Definir objetivo
    objetivo = "Implementar análise técnica completa do projeto NEXO"
    
    # Executar ciclo completo
    resultado = await bot.ciclo_completo(objetivo)
    
    # Visualizar resultado
    print(resultado)

# Executar
asyncio.run(main())
```

---

## 🎯 Fases Detalhadas

### FASE 1: PLANEJAR
```python
plano = await bot.planejar("Meu objetivo")
```

**Output:**
```json
{
  "objetivo": "Meu objetivo",
  "passos": [
    {"num": 1, "tarefa": "Verificar normas técnicas", "ferramenta": "verificar_normas"},
    {"num": 2, "tarefa": "Calcular orçamento", "ferramenta": "calcular_orcamento"},
    {"num": 3, "tarefa": "Analisar código", "ferramenta": "analisar_codigo"},
    {"num": 4, "tarefa": "Gerar relatório", "ferramenta": "gerar_relatorio"}
  ],
  "timestamp": "2026-01-20T...",
  "status": "PLANEJADO"
}
```

### FASE 2: AGIR
```python
resultado = await bot.agir(plano)
```

**Executa:**
1. Verificar normas técnicas (NBR-2026-A, ISO-9001-ENG, ...)
2. Calcular orçamento (R$ 250,00 × número de áreas)
3. Analisar código (complexidade, qualidade)
4. Gerar relatório consolidado com timestamp

**Output:**
```json
{
  "plano": "Meu objetivo",
  "execucoes": [
    {
      "passo": 1,
      "tarefa": "Verificar normas técnicas",
      "ferramenta": "verificar_normas",
      "resultado": ["NBR-2026-A", "ISO-9001-ENG", ...],
      "status": "SUCESSO"
    },
    ...
  ],
  "timestamp": "2026-01-20T..."
}
```

### FASE 3: OBSERVAR
```python
observacoes = await bot.observar(resultado)
```

**Analisa:**
- Total de tarefas: 4
- Tarefas com sucesso: 4
- Taxa de sucesso: 100%
- Próximas ações: Deploy, Sincronizar com HF, Iniciar novo ciclo

**Output:**
```json
{
  "timestamp": "2026-01-20T...",
  "analise": {
    "total_tarefas": 4,
    "tarefas_sucesso": 4,
    "tarefas_erro": 0,
    "taxa_sucesso": 100.0
  },
  "proximas_acoes": ["Fazer deploy", "Sincronizar com HF", "Iniciar novo ciclo"]
}
```

---

## 🔧 Componentes Disponíveis

### ConfigManager
```python
config = ConfigManager()

# Detectar ambiente
ambiente = config.detectar_ambiente()
# Saída: "local", "huggingface_spaces", ou "docker"

# Validar chaves
if config.validar_chaves():
    print("✅ Chaves configuradas corretamente")
```

### NexusEconomy
```python
economia = NexusEconomy()

# Calcular orçamento
orcamento = economia.calcular_orcamento(["arquitetura", "infraestrutura"])
print(f"Total: R$ {orcamento['total']}")  # R$ 500.00 (2 áreas × R$ 250)

# Verificar normas
normas = economia.verificar_normas("engineering")
print(normas)  # ["NBR-2026-A", "ISO-9001-ENG", "ISO-14001"]
```

### ToolsManager
```python
tools = bot.tools

# Chamar ferramenta diretamente
resultado = tools.ferramentas['calcular_orcamento'](["web", "mobile", "backend"])

# Listar ferramentas disponíveis
print(tools.ferramentas.keys())
# dict_keys(['calcular_orcamento', 'verificar_normas', 'gerar_relatorio', 'analisar_codigo', 'buscar_informacoes'])
```

---

## 💾 Memória Persistente

### Histórico de Ações
```python
# Acessar histórico
historico = bot.historico_acoes

# Contar ciclos executados
print(f"Total de ciclos: {len(historico)}")

# Última ação
ultima_acao = historico[-1]
print(ultima_acao['timestamp'])
```

Arquivo salvo em: `/workspaces/rodolfo/data/historico_acoes.json`

### Contexto Acumulado
```python
# Acessar contexto
contexto = bot.contexto_acumulado

# Ver resultados de ferramentas
print(contexto['verificar_normas'])
print(contexto['calcular_orcamento'])
```

---

## 🔄 Loop Contínuo

O bot pode executar ciclos continuamente:

```python
async def main():
    bot = BotEngenheiroNexo()
    
    ciclo_num = 1
    while True:
        print(f"🔄 CICLO #{ciclo_num}")
        await bot.ciclo_completo("Executar análise periódica")
        
        # Aguardar 5 minutos
        print("⏳ Aguardando 5 minutos...")
        await asyncio.sleep(300)
        
        ciclo_num += 1

asyncio.run(main())
```

---

## 📊 Acesso à IA (ChatGroq)

O bot usa a IA para gerar correções automáticas:

```python
# Gerar correção para um erro
codigo_corrigido = await bot.gerar_correcao_ia(
    codigo_atual="...",
    erro_descricao="ModuleNotFoundError: No module named 'langchain'"
)

print(codigo_corrigido)
```

---

## 🌐 Variáveis de Ambiente

Configure no `.env`:

```env
# Essencial
GROQ_API_KEY=gsk_...
HF_TOKEN=hf_...

# Opcional
GEMINI_API_KEY=...
PINECONE_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
```

---

## 🚀 Executar no Hugging Face Spaces

1. **Deploy**: O `requirements.txt` já tem `langchain`
2. **Configurar**: Adicione as chaves no `.env` do Space
3. **Iniciar**: O `bot_engenheiro_v2.py` executa automaticamente

---

## 📈 Status de Implementação

- ✅ Motor de Decisão (Planejar → Agir → Observar)
- ✅ ConfigManager (Detecção de Ambiente)
- ✅ NexusEconomy (Orçamento + Normas)
- ✅ ToolsManager (5 ferramentas disponíveis)
- ✅ Memória Persistente (Histórico + Contexto)
- ✅ Integração com ChatGroq
- ✅ Requirements.txt com todas as dependências
- ✅ Testes de sintaxe Python

---

**Criado em**: 20 de janeiro de 2026  
**Versão**: NEXO v2026  
**Status**: 🟢 PRONTO PARA PRODUÇÃO

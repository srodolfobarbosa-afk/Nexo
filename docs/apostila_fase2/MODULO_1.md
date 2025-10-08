Módulo 1 — Estrutura de Funcionamento Interno

Objetivo:

Ensinar a Manus como um sistema vivo de IA deve ser organizado em camadas, entendendo a lógica de funcionamento de cada parte.

Conteúdo:

1. Camadas do Sistema

- Infraestrutura — hospedagem (Vercel, Replit, GitHub Pages) para frontends; Render / Heroku / Docker para backends.
- Agentes operacionais — agentes especializados (EcoFinance, EcoBank, EcoEdu, EcoGrowth). Cada agente tem responsabilidades claras e API bem definida.
- Memória cognitiva — Supabase/Postgres para persistência, SQLite para fallback local, JSON para memória curta.
- Segurança — autenticação (Supabase Auth / OIDC), tokens, roles e auditoria.

2. Fluxo de Conexão

- Ordem: Usuário → Entrada (API/Chat)
- Distribuição: Nexo (orquestrador) decide qual agente processa
- Execução: Agente executa ação com ferramentas
- Memória: Resultado gravado em EcoMemory
- Relatório: Resultado retornado ao usuário e registrado em logs

Exercício Prático:

Crie um mapa mental conectando: “Usuário dá comando” → “Agente executa” → “Dados gravados na memória” → “Relatório exibido”.

Script auxiliar: `scripts/apostila/exercicio_1_map.py` (gera um JSON de exemplo com o fluxo)

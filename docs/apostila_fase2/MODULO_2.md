Módulo 2 — Organização de Dados e Memória

Objetivo:

Fazer Manus entender como guardar, buscar e usar informações para aprender com o tempo.

Conteúdo:

1. Tipos de Dados

- Conversas: histórico de interação com usuários
- Decisões: ações tomadas e razões (metadados)
- Erros corrigidos: logs de falhas e correções aplicadas
- Resultados financeiros: transações, receitas, despesas

2. Persistência

- Banco principal: Supabase (Postgres)
- Fallback: SQLite local
- Memória curta: JSON em disco

3. Consultas Inteligentes

Sempre perguntar antes de agir:
- "Já vi isso antes?"
- "Qual foi o resultado da última vez?"
- "O que devo mudar desta vez?"

Exercício Prático:

Criar um log fictício de 5 interações e rodar `scripts/apostila/exercicio_2_memory.py` para mostrar como consultar o passado antes de agir.

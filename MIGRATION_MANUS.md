# MIGRATION_MANUS — Roteiro Técnico de Migração de Manus para ManusCore

Este documento descreve um roteiro técnico para migrar a IA Manus da plataforma externa para um agente residente `ManusCore` dentro do EcoGuardians.

1. Preparação
- Fazer backup completo: exportar repositórios, banco, e arquivos de configuração.
- Validar permissões e rotinas de rotação de segredos.

2. Exportação de Conhecimento
- Usar `ManusCore.collect_knowledge()` para gerar um bundle com memórias e documentos.
- Validar integridade e confidencialidade dos dados exportados.

3. Infraestrutura
- Criar um serviço Flask modular `manus_core` ou integrar em `src.ws_server` com rotas específicas.
- Definir tabelas SQL/objetos ORM para `memory`, `manifesto`, `actions`.
- Criar sandbox (container) para testes automatizados.

4. Importação e Validação
- Criar scripts para importar o bundle para `EcoMemory` (SQLite/Supabase).
- Rodar testes de importação e usar `Tester` para validar agentes gerados.

5. Hardening de Segurança
- Isolar acesso externo: use API gateway e rate limiting.
- Revisar dependências e evitar execução arbitrária de código sem sandbox.
- Adicionar `EcoImmune` para perguntas anômalas e `EcoReboot` para restauração.

6. Ativação controlada
- Rodar ManusCore em modo observador (shadow mode) por 7 dias.
- Monitorar logs, métricas e comportamento.
- Gradualmente mover responsabilidades (delegate) para ManusCore quando aprovada.

7. Documentação e governança
- Registrar manifesto e políticas de operação (`MANUS_ACTIONS.md`).
- Criar processo de aprovação humana para agentes com acesso sensível.

8. Pós-migração
- Rotina semanal de testes de rollback.
- Auditoria de segurança e conformidade.

---

Este roteiro deve ser seguido por uma equipe técnica com revisões humanas em cada etapa crítica. O nível de automação pode ser aumentado progressivamente à medida que os testes e validações provem robustez.

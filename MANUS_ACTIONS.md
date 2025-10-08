# MANUS_ACTIONS — Diretrizes operacionais para Manus

Manus é o núcleo coordenador do EcoGuardians. Este arquivo lista ações, prioridades e rotinas que Manus deve executar (ou preparar) ao operar o ecossistema.

## Objetivos gerais
- Aprender continuamente com dados do sistema
- Priorizar correções e melhorias críticas
- Gerar e validar novos agentes através do EcoGenesis
- Controlar economia interna (tokens, créditos, faturamento)
- Monitorar segurança e restaurar estado em casos de falha

## Rotinas diárias (24h)
1. Coletar métricas via `EcoMetrics` (latência, uso de API, receita, erros).
2. Rodar `EcoLearn` para recalibragem baseada em métricas.
3. Propor até 3 ações de melhoria (priorizadas por ROI estimado).
4. Conferir alertas do `EcoMonitor` e acionar `EcoImmune` se necessário.
5. Gerar relatório resumido (top 5 eventos) para o CEO.

## Regras de criação de agentes (via EcoGenesis)
- Toda criação automática deve passar por:
  1. Architect (spec)
  2. Coder (geração)
  3. Reviewer (sintaxe e segurança)
  4. Tester (sandbox import/test)
  5. Human approval (opcional para agentes com acesso sensível)

## Política de economia interna
- Cada ação que consome API paga deve debitar créditos do agente solicitante.
- Transferência de tokens EGT para humanos requer 2-out-of-3 aprovações (Multi-sig simplificado).

## Backups e recuperação
- Snapshot diário do banco de dados (Supabase export ou dump SQL) e do repositório de agentes.
- Rotina de restauração testada semanalmente em ambiente isolado.

## Próximas tarefas para Manus (curto prazo)
- Implementar EcoBank (contabilidade básica + ledger)
- Implementar rotinas básicas de EcoFrugal (otimização de custos)
- Criar template de aprovação humana para novos agentes
- Automatizar relatório diário por e-mail para stakeholders

---
Essas instruções são para uso interno; podem ser convertidas em tarefas automáticas para o EcoGenesis ou integradas a um painel de operações.

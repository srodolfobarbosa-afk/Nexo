Visão: Autoconstrução de agentes

Objetivo
- Documentar a visão e o esqueleto para que os agentes do repositório atuem como um organismo vivo de auto-construção e auto-evolução.

Componentes propostos
- Orquestrador de Intenções: um serviço que recebe "intents" e direciona tarefas para agentes apropriados.
- Agentes modulares: cada agente (ex.: Analyst, Coder, Executor) expõe uma interface padrão para receber tarefas, executar (usando LLMs ou ferramentas) e reportar resultados.
- Pipeline de integração contínua para agentes: testes automatizados, validação de segurança e deploy contínuo.

Integração com IA de código aberto
- Preparar hooks para integração com modelos locais (ex.: Llama/llama-cpp/ggml) e APIs.
- Definir formatos de dados e contratos (JSON Schema) para mensagens entre agentes.

Próximos passos
- Implementar um protótipo do orquestrador e um agente mínimo (hello-world) que execute uma tarefa simples.
- Criar testes end-to-end que exercitem o ciclo: intenção → agente → código gerado → execução segura.

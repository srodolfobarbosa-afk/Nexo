import importlib
import os
from core.auto_construction import safe_json_response

from communication_manager import notify_user

class GenesisAgentBuilder:
    def __init__(self, llm_caller):
        self.llm_caller = llm_caller
        self.agents = {}

    def build_agent(self, agent_spec):
        """
        Recebe uma especificação (JSON) do agente a ser criado, incluindo nome, ferramentas, lógica, etc.
        Usa LLM para gerar o código do agente e integra ao sistema.
        """
        prompt = f"""
        Crie o código Python para um agente chamado '{agent_spec['name']}' com as seguintes ferramentas: {agent_spec.get('tools', [])}.
        O agente deve ser capaz de analisar, executar tarefas e se auto-corrigir. Implemente métodos para comunicação com outros agentes e para enviar mensagens ao usuário (via notify_user). Permita que o agente faça perguntas objetivas sobre objetivos e ações.
        Responda apenas com o código Python do agente, sem explicações.
        """
        response = self.llm_caller(prompt)
        agent_code = safe_json_response(response, fallback_response={"code": "# Erro ao gerar agente"}).get("code", "")
        if agent_code and "class" in agent_code:
            file_path = f"agentes/{agent_spec['name']}.py"
            # Salva o código convertendo \n para quebras de linha reais
            with open(file_path, "w") as f:
                f.write(agent_code.replace("\\n", "\n"))
            # Carrega dinamicamente o agente
            module_name = f"agentes.{agent_spec['name']}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            agent_class = getattr(module, agent_spec['name'], None)
            if agent_class:
                self.agents[agent_spec['name']] = agent_class()
                print(f"Agente '{agent_spec['name']}' criado e integrado.")
                return self.agents[agent_spec['name']]
        print(f"Falha ao criar agente '{agent_spec['name']}'.")
        return None

    def list_agents(self):
        return list(self.agents.keys())

    def communicate(self, sender, receiver, message):
        if sender in self.agents and receiver in self.agents:
            return self.agents[receiver].receive_message(sender, message)
        return f"Agente '{receiver}' não encontrado."

    def agent_notify_user(self, agent_name, message, subject=None):
        if agent_name in self.agents:
            notify_user(f"[{agent_name}] {message}", subject or f"Nexo: Mensagem do agente {agent_name}")
            print(f"Mensagem enviada pelo agente '{agent_name}' ao usuário.")
        else:
            print(f"Agente '{agent_name}' não encontrado para notificação.")

# Exemplo de uso:
if __name__ == "__main__":
    def dummy_llm(prompt):
        # Simula resposta do LLM gerando um agente básico
        return '{"code": "class DummyAgent:\n    def __init__(self):\n        self.name = \'DummyAgent\'\n    def receive_message(self, sender, message):\n        return f\'Recebido de {sender}: {message}\'"}'
    builder = GenesisAgentBuilder(dummy_llm)
    spec = {"name": "DummyAgent", "tools": ["internet_search", "self_correction"]}
    agent = builder.build_agent(spec)
    print(builder.list_agents())
    print(builder.communicate("DummyAgent", "DummyAgent", "Olá agente!"))

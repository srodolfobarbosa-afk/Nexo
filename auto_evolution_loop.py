import os
import time
import json
from dotenv import load_dotenv
from communication_manager import notify_user
from genesis_agent_builder import GenesisAgentBuilder
from debate_environment import DebateEnvironment
from tool_builder import ToolBuilder

# Carrega variáveis do .env (opcional)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)


def dummy_llm(prompt: str) -> dict:
    """LLM de teste que retorna um snippet de código em JSON (simulado)."""
    import re

    match = re.search(r"um agente chamado '([^']+)'", prompt)
    agent_name = match.group(1) if match else "AgenteGenerico"
    code = f"""{{"code": "class {agent_name}:\n    def __init__(self):\n        self.name = '{agent_name}'\n\n    def falar(self, problema):\n        return f\"{agent_name} analisou: {{problema}}\""}}"""
    try:
        return json.loads(code)
    except Exception:
        return {"code": code}


def validar_chaves_api() -> tuple[dict, dict]:
    provedores = [
        ("google", os.getenv("GOOGLE_API_KEY")),
        ("openai", os.getenv("OPENAI_API_KEY")),
        ("groq", os.getenv("GROQ_API_KEY")),
        ("gemini", os.getenv("GEMINI_API_KEY")),
    ]
    chaves_validas = {}
    chaves_invalidas = {}
    for nome, chave in provedores:
        if chave and testar_chave(nome, chave):
            chaves_validas[nome] = chave
        else:
            chaves_invalidas[nome] = chave
    return chaves_validas, chaves_invalidas


def testar_chave(provedor: str, chave: str) -> bool:
    # Implementação simples: presença da chave indica válida.
    return bool(chave)


def obter_provedor_prioritario():
    ordem = os.getenv("NEXO_LLM_PROVIDER", "google,openai,groq,gemini").split(',')
    chaves_validas, chaves_invalidas = validar_chaves_api()
    for prov in ordem:
        if prov in chaves_validas:
            return prov, chaves_validas[prov]
    return None, None


def buscar_memoria_curto_prazo():
    memoria_path = os.path.join(os.path.dirname(__file__), 'memoria_curto_prazo.json')
    if os.path.exists(memoria_path):
        with open(memoria_path, 'r') as f:
            try:
                dados = json.load(f)
                print(f"Memória de curto prazo carregada: {dados}")
                return dados
            except Exception as e:
                print(f"Erro ao carregar memória: {e}")
    else:
        print("Nenhuma memória de curto prazo encontrada.")
    return {}


def registrar_memoria_curto_prazo(dados):
    memoria_path = os.path.join(os.path.dirname(__file__), 'memoria_curto_prazo.json')
    try:
        with open(memoria_path, 'w') as f:
            json.dump(dados, f)
        print("Memória de curto prazo registrada.")
    except Exception as e:
        print(f"Erro ao registrar memória: {e}")


def plano_acao_humana(chaves_invalidas):
    print("\nPlano de ação necessário!")
    mensagem = "Nexo precisa de intervenção humana:\n"
    for prov, chave in chaves_invalidas.items():
        mensagem += f"- Provedor {prov} com chave inválida: {chave}\n  > Gere uma nova chave de API para o serviço {prov} e atualize o arquivo .env.\n"
        print(f"- Provedor {prov} com chave inválida: {chave}")
        print(f"  > Gere uma nova chave de API para o serviço {prov} e atualize o arquivo .env.")
    notify_user(mensagem, subject="Nexo: Ação Humana Necessária")
    print("Aguardando resposta do usuário... Nexo continuará evoluindo e estudando enquanto espera.")
    while True:
        try:
            resposta = input("Digite 'ok' quando resolver o problema ou pressione Enter para continuar estudando: ")
        except Exception:
            resposta = ''
        if resposta.strip().lower() == 'ok':
            print("Chaves atualizadas. Retomando fluxo principal.")
            break
        else:
            print("Nexo está estudando, evoluindo ou se auto-corrigindo enquanto aguarda...")
            time.sleep(5)


def auto_construir_ferramenta(problema, descricao):
    """Solicita ao ToolBuilder a criação de uma ferramenta sob demanda usando o LLM."""
    tb = ToolBuilder()
    prompt = f"Crie uma função Python que resolva o seguinte problema: {descricao}. O problema detectado foi: {problema}"
    resposta = dummy_llm(prompt)
    code = resposta.get('code') if isinstance(resposta, dict) else None
    if not code:
        print("[Auto-Construção] LLM não retornou código válido.")
        return None
    try:
        nome_ferramenta = f"tool_{int(time.time())}"
        tb.create_tool(nome_ferramenta, code)
        print(f"[Auto-Construção] Ferramenta '{nome_ferramenta}' criada e registrada.")
        return nome_ferramenta
    except Exception as e:
        print(f"[Auto-Construção] Falha ao criar ferramenta: {e}")
    return None


def auto_evolution_loop():
    """Loop principal consolidado e sem duplicações."""
    # Tenta usar NexoGenesis se disponível, senão usa apenas o agent builder
    nexo_genesis = None
    try:
        from agentes.NexoGenesis import NexoGenesisAgent

        nexo_genesis = NexoGenesisAgent()
    except Exception:
        nexo_genesis = None

    agent_builder = GenesisAgentBuilder(dummy_llm)
    ciclo = 0
    memoria_curto_prazo = buscar_memoria_curto_prazo()

    agentes_nomes = ["Analyzer", "Executor", "Reviewer", "Memory"]
    # Garante que agentes essenciais existam
    for nome in agentes_nomes:
        if nome not in agent_builder.list_agents():
            spec = {"name": nome, "tools": ["internet_search", "self_correction"]}
            agent_builder.build_agent(spec)

    agentes = [agent_builder.agents.get(nome) for nome in agentes_nomes if nome in agent_builder.agents]
    debate_env = DebateEnvironment(agentes)

    while True:
        print(f"\n--- CICLO {ciclo} DE AUTO-EVOLUÇÃO ---")
        provedor, chave = obter_provedor_prioritario()
        memoria_curto_prazo['ultimo_provedor'] = provedor
        memoria_curto_prazo['ciclo'] = ciclo

        if not provedor:
            _, chaves_invalidas = validar_chaves_api()
            print("Chaves de API inválidas ou ausentes; solicitando ação humana.")
            plano_acao_humana(chaves_invalidas)
            # após intervenção, continua o loop
            time.sleep(1)
            ciclo += 1
            continue

        print(f"Provedor de IA selecionado: {provedor}")

        # Execução do módulo de evolução, se presente
        if nexo_genesis:
            try:
                nexo_genesis.evolution_module.evolve()
                evolucao_status = nexo_genesis.evolution_module.get_evolution_status()
                memoria_curto_prazo['evolucao'] = evolucao_status
                nexo_genesis.save_to_memory("NexoGenesis", f"evolucao_ciclo_{ciclo}", evolucao_status)
            except Exception as e:
                print(f"Erro na evolução: {e}")

        # Periodicamente tenta auto-construção
        if ciclo % 2 == 0:
            try:
                nome_tool = auto_construir_ferramenta(f"Ciclo {ciclo}", "Exemplo de ferramenta gerada")
                if nome_tool:
                    memoria_curto_prazo.setdefault('ferramentas', {})[nome_tool] = {
                        'descricao': 'gerada automaticamente', 'ciclo': ciclo
                    }
            except Exception as e:
                print(f"Falha na auto-construção: {e}")

        registrar_memoria_curto_prazo(memoria_curto_prazo)
        print(f"[LOG] Memória registrada: ciclo {ciclo}, provedor {provedor}")
        ciclo += 1
        time.sleep(5)


if __name__ == "__main__":
    auto_evolution_loop()
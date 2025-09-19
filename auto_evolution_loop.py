# Função para priorizar provedores conforme .env
def obter_provedor_prioritario():
    ordem = os.getenv('NEXO_LLM_PROVIDER', 'google,openai,groq,gemini').split(',')
    chaves_validas, chaves_invalidas = validar_chaves_api()
    for prov in ordem:
        if prov in chaves_validas:
            return prov, chaves_validas[prov]
    return None, None

# ========================
# IMPORTS E CONFIG GLOBAL
import os
import time
import json
from dotenv import load_dotenv
from communication_manager import notify_user
from genesis_agent_builder import GenesisAgentBuilder
from debate_environment import DebateEnvironment

# Carrega variáveis do .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# ========================
# FUNÇÕES DE AGENTES E LLM
def dummy_llm(prompt):
    import re
    import json
    # Extrai nome do agente do prompt
    match = re.search(r"um agente chamado '([^']+)'", prompt)
    agent_name = match.group(1) if match else "AgenteGenerico"
    code = f'''class {agent_name}:
    def __init__(self):
        self.name = '{agent_name}'

    def falar(self, problema):
        return f"{agent_name} analisou: {{problema}}"
'''
    return json.dumps({"code": code})

# Função para validar chaves de API
def validar_chaves_api():
    provedores = [
        ('google', os.getenv('GOOGLE_API_KEY')),
        ('openai', os.getenv('OPENAI_API_KEY')),
        ('groq', os.getenv('GROQ_API_KEY')),
        ('gemini', os.getenv('GEMINI_API_KEY'))
    ]
    chaves_validas = {}
    chaves_invalidas = {}
    for nome, chave in provedores:
        if chave and testar_chave(nome, chave):
            chaves_validas[nome] = chave
        else:
            chaves_invalidas[nome] = chave
    return chaves_validas, chaves_invalidas

def testar_chave(provedor, chave):
    return bool(chave)

def obter_provedor_prioritario():
    ordem = os.getenv('NEXO_LLM_PROVIDER', 'google,openai,groq,gemini').split(',')
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
        resposta = input("Digite 'ok' quando resolver o problema ou pressione Enter para continuar estudando: ")
        if resposta.strip().lower() == 'ok':
            print("Chaves atualizadas. Retomando fluxo principal.")
            break
        else:
            print("Nexo está estudando, evoluindo ou se auto-corrigindo enquanto aguarda...")
            time.sleep(5)

# ========================
# LOOP PRINCIPAL
def auto_evolution_loop():
    agent_builder = GenesisAgentBuilder(dummy_llm)
    ciclo = 0
    memoria_curto_prazo = buscar_memoria_curto_prazo()
    agentes_nomes = ["Analyzer", "Executor", "Reviewer", "Memory"]
    agentes = []
    for nome in agentes_nomes:
        if nome not in agent_builder.list_agents():
            spec = {"name": nome, "tools": ["internet_search", "self_correction"]}
            agent_builder.build_agent(spec)
    for nome in agentes_nomes:
        agente = agent_builder.agents.get(nome)
        if agente:
            agentes.append(agente)
    debate_env = DebateEnvironment(agentes)
    while True:
        print("\n--- Loop de Auto-Evolução ---")
        provedor, chave = obter_provedor_prioritario()
        if not provedor:
            _, chaves_invalidas = validar_chaves_api()
            problema = "Necessidade de decisão: Chaves de API inválidas ou contexto indefinido."
            print(f"Nexo Gênesis: Reunião iniciada para o problema: {problema}")
            if not debate_env.agents:
                print("Sala de reunião vazia. Nexo está construindo agentes reais...")
                for nome in agentes_nomes:
                    if nome not in agent_builder.list_agents():
                        spec = {"name": nome, "tools": ["internet_search", "self_correction"]}
                        agent_builder.build_agent(spec)
                agentes = [agent_builder.agents[nome] for nome in agentes_nomes if nome in agent_builder.agents]
                debate_env = DebateEnvironment(agentes)
            falas = debate_env.debate(problema)
            print("Nexo Gênesis: Decisão tomada com base nas análises dos agentes.")
            mensagem = f"Atenção: {problema} Necessária ação manual para resolver."
            notify_user(mensagem, subject="Nexo: Decisão Coletiva - Ação Manual")
            plano_acao_humana(chaves_invalidas)
            continue
        print(f"Provedor de IA selecionado: {provedor}")
        memoria_curto_prazo['ultimo_provedor'] = provedor
        memoria_curto_prazo['ciclo'] = ciclo
        registrar_memoria_curto_prazo(memoria_curto_prazo)
        if not debate_env.agents:
            print("Sala de reunião vazia. Nexo está construindo agentes reais...")
            for nome in agentes_nomes:
                if nome not in agent_builder.list_agents():
                    spec = {"name": nome, "tools": ["internet_search", "self_correction"]}
                    agent_builder.build_agent(spec)
            agentes = [agent_builder.agents[nome] for nome in agentes_nomes if nome in agent_builder.agents]
            debate_env = DebateEnvironment(agentes)
        debate_env.debate(f"Ciclo {ciclo}: Evolução do sistema e uso do provedor {provedor}")
        if ciclo % 3 == 0:
            spec = {"name": f"AgenteAuto{ciclo}", "tools": ["internet_search", "self_correction"]}
            agent_builder.build_agent(spec)
        print(f"Agentes atuais: {agent_builder.list_agents()}")
        if ciclo % 5 == 0:
            print("Nexo: Planejando receitas e despesas para manter o sistema auto-evolutivo.")
            notify_user("Precisamos evoluir o modelo de negócio para garantir recursos e manter o sistema autônomo.", subject="Nexo: Planejamento Financeiro")
        ciclo += 1
        time.sleep(5)

if __name__ == "__main__":
    auto_evolution_loop()

def buscar_memoria_curto_prazo():
    # Simula busca em banco de dados local (JSON)
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

def auto_evolution_loop():
    analyzer = Analyzer()
    executor = Executor()
    memory = Memory()
    agent_builder = GenesisAgentBuilder(dummy_llm)  # Substitua dummy_llm pelo LLM real
    ciclo = 0
    memoria_curto_prazo = buscar_memoria_curto_prazo()
    while True:
        print("\n--- Loop de Auto-Evolução ---")
        provedor, chave = obter_provedor_prioritario()
        # Situação que exige decisão coletiva (exemplo: falta de chave, permissão, dúvida, contexto, etc)
        if not provedor:
            _, chaves_invalidas = validar_chaves_api()
            problema = "Necessidade de decisão: Chaves de API inválidas ou contexto indefinido."
            print(f"Nexo: {problema} Quem tem uma solução?")
            analyzer_resposta = analyzer.run() if hasattr(analyzer, 'run') else "Analyzer: Análise realizada."
            print(f"Analyzer: {analyzer_resposta if analyzer_resposta else 'Análise realizada.'}")
            reviewer_resposta = "O plano é seguro e faz sentido. Eu o aprovo."
            print(f"Reviewer: {reviewer_resposta}")
            executor_resposta = executor.run() if hasattr(executor, 'run') else "Executor: Pronto para executar a ação."
            print(f"Executor: {executor_resposta if executor_resposta else 'Pronto para executar a ação.'}")
            print("Nexo: Plano aprovado. Executor, inicie a notificação.")
            mensagem = f"Atenção: {problema} Necessária ação manual para resolver."
            notify_user(mensagem, subject="Nexo: Decisão Coletiva - Ação Manual")
            plano_acao_humana(chaves_invalidas)
            continue
        print(f"Provedor de IA selecionado: {provedor}")
        memoria_curto_prazo['ultimo_provedor'] = provedor
        memoria_curto_prazo['ciclo'] = ciclo
        registrar_memoria_curto_prazo(memoria_curto_prazo)
        analyzer.run()
        executor.run()
        memory.run()
        # Genesis cria agentes autônomos
        if ciclo % 3 == 0:
            spec = {"name": f"AgenteAuto{ciclo}", "tools": ["internet_search", "self_correction"]}
            agent_builder.build_agent(spec)
        print(f"Agentes atuais: {agent_builder.list_agents()}")
        # Planejamento financeiro futuro
        if ciclo % 5 == 0:
            print("Nexo: Planejando receitas e despesas para manter o sistema auto-evolutivo.")
            notify_user("Precisamos evoluir o modelo de negócio para garantir recursos e manter o sistema autônomo.", subject="Nexo: Planejamento Financeiro")
        ciclo += 1
        time.sleep(5)  # Intervalo entre ciclos

if __name__ == "__main__":
    auto_evolution_loop()

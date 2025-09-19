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
from tool_builder import ToolBuilder

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
# LOOP PRINCIPAL AUTOMÁTICO E ORGANIZADO
def auto_evolution_loop():
    from agentes.NexoGenesis import NexoGenesisAgent
    nexo_genesis = NexoGenesisAgent()
    ciclo = 0
    memoria_curto_prazo = buscar_memoria_curto_prazo()
    while True:
        print(f"\n--- CICLO {ciclo} DE AUTO-EVOLUÇÃO ---")
        provedor, chave = obter_provedor_prioritario()
        memoria_curto_prazo['ultimo_provedor'] = provedor
        memoria_curto_prazo['ciclo'] = ciclo
        # Evolução contínua
        print("🧬 [NexoGenesis] Executando ciclo de evolução...")
        try:
            nexo_genesis.evolution_module.evolve()
            evolucao_status = nexo_genesis.evolution_module.get_evolution_status()
            memoria_curto_prazo['evolucao'] = evolucao_status
            nexo_genesis.save_to_memory("NexoGenesis", f"evolucao_ciclo_{ciclo}", evolucao_status)
            # Registrar tentativa de evolução
            nexo_genesis.log_evolution_attempt(
                cycle_number=ciclo,
                mission_prompt=evolucao_status.get('mission_prompt', f"Ciclo {ciclo}"),
                llm_response_raw=evolucao_status,
                success=evolucao_status.get('success', True),
                reason_for_failure=evolucao_status.get('reason_for_failure'),
                details=evolucao_status
            )
        except Exception as e:
            print(f"Erro na evolução: {e}")
            # Registrar tentativa de evolução com falha
            nexo_genesis.log_evolution_attempt(
                cycle_number=ciclo,
                mission_prompt=f"Ciclo {ciclo}",
                llm_response_raw=str(e),
                success=False,
                reason_for_failure=str(e),
                details=None
            )
        # Auto-construção proativa
        if ciclo % 2 == 0:
            print("🛠️ [NexoGenesis] Auto-construção proativa de funcionalidade...")
            try:
                resultado = nexo_genesis.auto_constructor.auto_construct_feature(f"Nova funcionalidade ciclo {ciclo}")
                memoria_curto_prazo['auto_construcao'] = resultado
                nexo_genesis.save_to_memory("NexoGenesis", f"auto_construcao_ciclo_{ciclo}", resultado)
                if resultado.get("success"):
                    print(f"[LOG] Ferramenta criada: {resultado}")
                else:
                    print(f"[LOG] Falha na auto-construção: {resultado}")
            except Exception as e:
                print(f"Erro na auto-construção: {e}")
        # Planejamento financeiro futuro
        if ciclo % 5 == 0:
            print("💸 [NexoGenesis] Planejando receitas e despesas para manter o sistema auto-evolutivo.")
            notify_user("Precisamos evoluir o modelo de negócio para garantir recursos e manter o sistema autônomo.", subject="Nexo: Planejamento Financeiro")
        # Registrar memória local
        registrar_memoria_curto_prazo(memoria_curto_prazo)
        # Exibir log detalhado
        print(f"[LOG] Memória registrada: ciclo {ciclo}, provedor {provedor}")
        print(f"[LOG] Status evolução: {memoria_curto_prazo.get('evolucao',{})}")
        print(f"[LOG] Status auto-construção: {memoria_curto_prazo.get('auto_construcao',{})}")
        ciclo += 1
        time.sleep(10)

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
        if not provedor:
            _, chaves_invalidas = validar_chaves_api()
            problema = "Necessidade de decisão: Chaves de API inválidas ou contexto indefinido."
            print(f"Nexo: {problema} Quem tem uma solução?")
            # O Analyzer sempre tenta gerar um plano, mesmo se o LLM falhar ou vier incompleto
            try:
                resposta = analyzer.falar(problema)
                print(f"Analyzer: {resposta}")
                # Se o plano não tiver 'approved', registra falha mas segue
                if isinstance(resposta, str) and 'approved' not in resposta:
                    print("[LOG] Resposta do LLM incompleta. Falha registrada, mas Nexo continua execução.")
            except Exception as e:
                print(f"[LOG] Falha ao obter plano do Analyzer: {e}. Gerando plano padrão.")
                resposta = analyzer.default_correction_plan(problema)
                print(f"Analyzer (plano padrão): {resposta}")
            # O Reviewer e Executor seguem normalmente
            reviewer = Reviewer()
            print(f"Reviewer: {reviewer.falar(problema)}")
            print(f"Executor: {executor.falar(problema)}")
            print("Nexo: Notificando usuário sobre ação manual necessária.")
            mensagem = f"Atenção: {problema} Necessária ação manual para resolver."
            notify_user(mensagem, subject="Nexo: Decisão Coletiva - Ação Manual")
            plano_acao_humana(chaves_invalidas)
            continue
        print(f"Provedor de IA selecionado: {provedor}")
        memoria_curto_prazo['ultimo_provedor'] = provedor
        memoria_curto_prazo['ciclo'] = ciclo
        registrar_memoria_curto_prazo(memoria_curto_prazo)
        # O Analyzer sempre tenta gerar plano, nunca trava por falta de 'approved'
        problema = f"Ciclo {ciclo}: Evolução do sistema e uso do provedor {provedor}"
        try:
            resposta = analyzer.falar(problema)
            print(f"Analyzer: {resposta}")
            # Nexo nunca espera aprovação explícita. Se resposta for incompleta, assume liderança e segue.
            if (isinstance(resposta, str) and 'approved' not in resposta) or not resposta:
                print("[LOG] Resposta do LLM incompleta ou ausente. Nexo assume liderança, gera plano padrão e continua.")
                resposta = analyzer.default_correction_plan(problema)
                print(f"Analyzer (plano padrão): {resposta}")
        except Exception as e:
            print(f"[LOG] Falha ao obter plano do Analyzer: {e}. Nexo assume liderança, gera plano padrão e continua.")
            resposta = analyzer.default_correction_plan(problema)
            print(f"Analyzer (plano padrão): {resposta}")

        # Etapa de Auto-Construção com persistência
        erro_detectado = None
        if isinstance(resposta, str) and 'Invalid URL' in resposta:
            erro_detectado = 'Invalid URL'
            print(f"[Auto-Construção] Erro detectado: {erro_detectado}. Verificando memória de ferramentas...")
            ferramentas_registradas = memoria_curto_prazo.get('ferramentas', {})
            descricao_ferramenta = 'Valide se uma URL é válida e começa com http ou https'
            # Verifica se já existe ferramenta equivalente
            ferramenta_existente = None
            for nome, info in ferramentas_registradas.items():
                if info.get('descricao') == descricao_ferramenta:
                    ferramenta_existente = nome
                    break
            if ferramenta_existente:
                print(f"[Auto-Construção] Ferramenta já existente: {ferramenta_existente}. Usando ferramenta registrada.")
            else:
                print(f"[Auto-Construção] Solicitando criação de ferramenta sob demanda.")
                nome_ferramenta = auto_construir_ferramenta(erro_detectado, descricao_ferramenta)
                if nome_ferramenta:
                    print(f"[Auto-Construção] Ferramenta '{nome_ferramenta}' criada e registrada.")
                    # Persiste ferramenta na memória, incluindo contexto, problema e código
                    if 'ferramentas' not in memoria_curto_prazo:
                        memoria_curto_prazo['ferramentas'] = {}
                    memoria_curto_prazo['ferramentas'][nome_ferramenta] = {
                        'descricao': descricao_ferramenta,
                        'erro': erro_detectado,
                        'ciclo': ciclo,
                        'codigo': 'registrado pelo tool_builder',
                        'contexto': problema
                    }
                    registrar_memoria_curto_prazo(memoria_curto_prazo)
                else:
                    print("[Auto-Construção] Falha ao criar ferramenta sob demanda.")

        # Sugestão: instalar ferramentas essenciais para auto-construção
        ferramentas_essenciais = [
            {'nome': 'db_manager', 'descricao': 'Ferramenta para manipulação de banco de dados SQLite'},
            {'nome': 'json_formatter', 'descricao': 'Ferramenta para reformatar e validar JSON'},
            {'nome': 'url_validator', 'descricao': 'Ferramenta para validar URLs'},
            {'nome': 'api_connector', 'descricao': 'Ferramenta para conectar e testar APIs externas'}
        ]
        if 'ferramentas' not in memoria_curto_prazo:
            memoria_curto_prazo['ferramentas'] = {}
        for f in ferramentas_essenciais:
            if f['nome'] not in memoria_curto_prazo['ferramentas']:
                memoria_curto_prazo['ferramentas'][f['nome']] = {
                    'descricao': f['descricao'],
                    'ciclo': ciclo,
                    'codigo': 'a ser gerado pelo tool_builder',
                    'contexto': 'essencial para auto-construção'
                }
        registrar_memoria_curto_prazo(memoria_curto_prazo)

        print(f"Executor: {executor.falar(problema)}")
        print(f"Memory: {memory.falar(problema)}")
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

def auto_construir_ferramenta(problema, descricao):
    """
    Solicita ao ToolBuilder a criação de uma ferramenta sob demanda usando o LLM.
    """
    tb = ToolBuilder()
    # Prompt para o LLM gerar código da ferramenta
    prompt = f"Crie uma função Python que resolva o seguinte problema: {descricao}. O problema detectado foi: {problema}"
    # Aqui, dummy_llm pode ser substituído pelo LLM real
    resposta = dummy_llm(prompt)
    try:
        resposta_json = json.loads(resposta)
        code = resposta_json.get('code')
        if code:
            nome_ferramenta = f"tool_{int(time.time())}"
            tb.create_tool(nome_ferramenta, code)
            print(f"[Auto-Construção] Ferramenta '{nome_ferramenta}' criada e registrada.")
            return nome_ferramenta
        else:
            print("[Auto-Construção] LLM não retornou código válido.")
    except Exception as e:
        print(f"[Auto-Construção] Falha ao processar resposta do LLM: {e}")
    return None

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
        if not provedor:
            _, chaves_invalidas = validar_chaves_api()
            problema = "Necessidade de decisão: Chaves de API inválidas ou contexto indefinido."
            print(f"Nexo: {problema} Quem tem uma solução?")
            # O Analyzer sempre tenta gerar um plano, mesmo se o LLM falhar ou vier incompleto
            try:
                resposta = analyzer.falar(problema)
                print(f"Analyzer: {resposta}")
                # Se o plano não tiver 'approved', registra falha mas segue
                if isinstance(resposta, str) and 'approved' not in resposta:
                    print("[LOG] Resposta do LLM incompleta. Falha registrada, mas Nexo continua execução.")
            except Exception as e:
                print(f"[LOG] Falha ao obter plano do Analyzer: {e}. Gerando plano padrão.")
                resposta = analyzer.default_correction_plan(problema)
                print(f"Analyzer (plano padrão): {resposta}")
            # O Reviewer e Executor seguem normalmente
            reviewer = Reviewer()
            print(f"Reviewer: {reviewer.falar(problema)}")
            print(f"Executor: {executor.falar(problema)}")
            print("Nexo: Notificando usuário sobre ação manual necessária.")
            mensagem = f"Atenção: {problema} Necessária ação manual para resolver."
            notify_user(mensagem, subject="Nexo: Decisão Coletiva - Ação Manual")
            plano_acao_humana(chaves_invalidas)
            continue
        print(f"Provedor de IA selecionado: {provedor}")
        memoria_curto_prazo['ultimo_provedor'] = provedor
        memoria_curto_prazo['ciclo'] = ciclo
        registrar_memoria_curto
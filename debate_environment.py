class DebateEnvironment:
    def __init__(self, agents):
        self.agents = agents  # Lista de instâncias de agentes

    def debate(self, problem):
        print(f"\n[Debate] Problema apresentado: {problem}")
        falas = []
        for agent in self.agents:
            fala = agent.falar(problem)
            print(f"{agent.name} diz: {fala}")
            falas.append((agent.name, fala))
        return falas

class AgenteBase:
    def __init__(self, nome):
        self.nome = nome
    def falar(self, problema):
        return f"Minha análise sobre '{problema}'..."

    def debate(self, problem):
        print(f"\n[Debate] Problema apresentado: {problem}")
        opinions = {}
        for agent in self.agents:
            opinion = agent.give_opinion(problem)
            print(f"{agent.name} diz: {opinion}")
            opinions[agent.name] = opinion
        return opinions

class Agent:
    def __init__(self, name):
        self.name = name
    def give_opinion(self, problem):
        # Cada agente pode ter lógica própria
        return f"Minha análise sobre '{problem}'... (simulação)"

# Exemplo de uso:
if __name__ == "__main__":
    analyzer = Agent("Analyzer")
    executor = Agent("Executor")
    reviewer = Agent("Reviewer")
    debate_env = DebateEnvironment([analyzer, executor, reviewer])
    problem = "Como otimizar o uso das chaves de API?"
    opinions = debate_env.debate(problem)
    # O Nexo Gênesis tomaria decisão baseada nas opiniões
    print("\nNexo Gênesis decide com base nas opiniões dos agentes.")

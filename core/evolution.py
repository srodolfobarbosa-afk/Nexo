import json
import os
import threading
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv

from core.auto_construction import AutoConstructionModule
from core.database import get_supabase_client
from core.internet_search import InternetSearchModule

load_dotenv()


class EvolutionModule:
    """
    Módulo de evolução contínua do Nexo Gênesis
    Sistema de auto-loop que monitora, aprende e evolui automaticamente
    """

    def __init__(self, nexo_genesis_agent):
        self.supabase = get_supabase_client()
        self.search = InternetSearchModule()
        self.nexo = nexo_genesis_agent
        self.auto_constructor = AutoConstructionModule(self.nexo.call_llm)

        self.evolution_history = []
        self.is_evolving = False
        self.evolution_thread = None

        # Configurações de evolução
        self.evolution_interval = 3600  # 1 hora em segundos
        self.max_daily_evolutions = 5
        self.learning_sources = [
            "python new features",
            "AI agent best practices",
            "flask optimization",
            "supabase updates",
            "automation trends",
        ]

    def start_evolution_loop(self):
        """
        Inicia o loop de evolução contínua em background
        """
        if not self.is_evolving:
            self.is_evolving = True
            self.evolution_thread = threading.Thread(
                target=self._evolution_loop, daemon=True
            )
            self.evolution_thread.start()
            print("🧬 Sistema de evolução contínua iniciado")

    def stop_evolution_loop(self):
        """
        Para o loop de evolução
        """
        self.is_evolving = False
        if self.evolution_thread:
            self.evolution_thread.join()
        print("🛑 Sistema de evolução contínua parado")

    def _evolution_loop(self):
        """
        Loop principal de evolução que roda em background
        """
        while self.is_evolving:
            try:
                # Verifica se é hora de evoluir
                if self._should_evolve():
                    print("🧬 Iniciando ciclo de evolução...")
                    self.evolve()

                # Aguarda próximo ciclo
                time.sleep(self.evolution_interval)

            except Exception as e:
                print(f"❌ Erro no loop de evolução: {e}")
                time.sleep(300)  # Aguarda 5 minutos em caso de erro

    def _should_evolve(self):
        """
        Determina se o sistema deve evoluir agora
        """
        # Verifica limite diário
        today = datetime.now().date()
        today_evolutions = [
            e
            for e in self.evolution_history
            if datetime.fromisoformat(e["timestamp"]).date() == today
        ]

        if len(today_evolutions) >= self.max_daily_evolutions:
            return False

        # Verifica se passou tempo suficiente desde última evolução
        if self.evolution_history:
            last_evolution = datetime.fromisoformat(
                self.evolution_history[-1]["timestamp"]
            )
            if datetime.now() - last_evolution < timedelta(
                seconds=self.evolution_interval
            ):
                return False

        return True

    def evolve(self):
        """
        Executa um ciclo completo de evolução
        """
        try:
            evolution_cycle = {
                "timestamp": datetime.now().isoformat(),
                "steps": [],
                "improvements": [],
                "errors": [],
            }

            # 1. Análise do estado atual
            current_state = self._analyze_current_state()
            evolution_cycle["steps"].append("analyze_state")

            # 2. Busca por melhorias
            improvements = self._search_for_improvements()
            evolution_cycle["steps"].append("search_improvements")

            # 3. Identifica oportunidades de evolução
            opportunities = self._identify_evolution_opportunities(
                current_state, improvements
            )
            evolution_cycle["steps"].append("identify_opportunities")

            # 4. Implementa melhorias (se houver)
            if opportunities:
                for opportunity in opportunities[:2]:  # Máximo 2 melhorias por ciclo
                    try:
                        result = self._implement_improvement(opportunity)
                        evolution_cycle["improvements"].append(result)
                        evolution_cycle["steps"].append(
                            f"implement_{opportunity['type']}"
                        )
                    except Exception as e:
                        evolution_cycle["errors"].append(str(e))

            # 5. Registra evolução
            self.evolution_history.append(evolution_cycle)
            self._save_evolution_log(evolution_cycle)

            print(
                f"✅ Ciclo de evolução concluído: {len(evolution_cycle['improvements'])} melhorias implementadas"
            )

        except Exception as e:
            print(f"❌ Erro no ciclo de evolução: {e}")

    def _analyze_current_state(self):
        """
        Analisa o estado atual do sistema
        """
        try:
            # Análise de performance
            performance_metrics = {
                "response_time": "normal",  # Seria medido em produção
                "error_rate": "baixa",
                "memory_usage": "normal",
            }

            # Análise de funcionalidades
            features_status = {
                "chat_interface": "ativo",
                "agent_creation": "ativo",
                "llm_integration": "ativo",
                "database_connection": "ativo",
            }

            # Análise de logs de erro (conceitual)
            recent_errors = []  # Seria extraído dos logs

            return {
                "performance": performance_metrics,
                "features": features_status,
                "errors": recent_errors,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    def _search_for_improvements(self):
        """
        Busca por melhorias e novas tecnologias
        """
        improvements = []

        for source in self.learning_sources:
            try:
                results = self.search.search_web(source, 2)
                for result in results:
                    content = self.search.scrape_content(result["link"])
                    if content:
                        improvements.append(
                            {
                                "source": source,
                                "title": result["title"],
                                "content": content["content"][
                                    :1000
                                ],  # Primeiros 1000 chars
                                "url": result["link"],
                            }
                        )
            except Exception as e:
                print(f"Erro ao buscar {source}: {e}")

        return improvements

    def _identify_evolution_opportunities(self, current_state, improvements):
        """
        Identifica oportunidades de evolução usando IA
        """
        prompt = f"""
        Você é o Evolution AI do ecossistema EcoGuardians.
        
        Estado atual do sistema:
        {json.dumps(current_state, indent=2)}
        
        Melhorias encontradas na internet:
        {json.dumps(improvements, indent=2)}
        
        Identifique oportunidades de evolução e retorne JSON com array de objetos:
        [
            {{
                "type": "performance|feature|security|optimization",
                "priority": "high|medium|low",
                "description": "descrição da melhoria",
                "implementation": "como implementar",
                "benefits": "benefícios esperados",
                "risks": "riscos potenciais"
            }}
        ]
        
        Foque em melhorias que:
        1. Aumentem a autonomia do sistema
        2. Melhorem a performance
        3. Adicionem funcionalidades úteis
        4. Sigam os princípios éticos do EcoGuardians
        
        Responda apenas com JSON válido.
        """

        try:
            response = self.nexo.call_llm(
                prompt, "Identificar oportunidades de evolução"
            )

            # Extrair JSON de forma robusta
            from core.json_utils import extract_json

            opportunities = extract_json(response)

            # Filtrar apenas oportunidades de alta e média prioridade
            return [
                op for op in opportunities if op.get("priority") in ["high", "medium"]
            ]

        except Exception as e:
            print(f"Erro ao identificar oportunidades: {e}")
            return []

    def _implement_improvement(self, opportunity):
        """
        Implementa uma melhoria específica
        """
        try:
            print(f"🔧 Implementando: {opportunity['description']}")

            # Usa o módulo de auto-construção para implementar
            result = self.auto_constructor.auto_construct_feature(
                f"{opportunity['type']}: {opportunity['description']} - {opportunity['implementation']}"
            )

            return {
                "opportunity": opportunity,
                "implementation_result": result,
                "status": "success" if result.get("success") else "failed",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "opportunity": opportunity,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat(),
            }

    def _save_evolution_log(self, evolution_cycle):
        """
        Salva log de evolução no banco de dados
        """
        try:
            # Salvar no Supabase (conceitual)
            # self.supabase.table("evolution_logs").insert(evolution_cycle).execute()

            # Salvar em arquivo local como backup
            log_file = f"logs/evolution_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs("logs", exist_ok=True)

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(evolution_cycle) + "\n")

        except Exception as e:
            print(f"Erro ao salvar log de evolução: {e}")

    def get_evolution_status(self):
        """
        Retorna status atual da evolução
        """
        return {
            "is_evolving": self.is_evolving,
            "total_evolutions": len(self.evolution_history),
            "last_evolution": (
                self.evolution_history[-1] if self.evolution_history else None
            ),
            "next_evolution_in": self.evolution_interval if self.is_evolving else None,
        }

    def force_evolution(self):
        """
        Força um ciclo de evolução imediato
        """
        if not self.is_evolving:
            print("🧬 Forçando evolução imediata...")
            self.evolve()
        else:
            print("⚠️ Sistema já está evoluindo automaticamente")

    def get_evolution_history(self):
        """
        Retorna histórico completo de evoluções
        """
        return self.evolution_history


if __name__ == "__main__":
    # Teste do módulo
    print("🧪 Testando módulo de evolução...")

    # Simulação de Nexo Genesis
    class MockNexoGenesis:
        def call_llm(self, prompt, context):
            return (
                '[{"type": "performance", "priority": "high", "description": "Teste"}]'
            )

    mock_nexo = MockNexoGenesis()
    evolution = EvolutionModule(mock_nexo)

    # Teste de evolução forçada
    evolution.force_evolution()
    print(f"Status: {evolution.get_evolution_status()}")

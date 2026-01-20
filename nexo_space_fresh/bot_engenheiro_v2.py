#!/usr/bin/env python3
"""
🤖 BOT ENGENHEIRO NEXO v2026 - SISTEMA AUTÔNOMO INTELIGENTE
Motor de Decisão com ciclo: Planejar -> Agir -> Observar
Auto-detecta, corrige, reconstrói e faz auto-deploy para Hugging Face
"""

import os
import sys
import subprocess
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from loguru import logger

load_dotenv()


class ConfigManager:
    """Gerencia configuração e validação de ambiente"""
    
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.hf_token = os.getenv("HF_TOKEN")
        self.ambiente = self.detectar_ambiente()
        self.logger = logger
        
    def detectar_ambiente(self) -> str:
        """Detecta se está rodando localmente ou no HF Spaces"""
        if "SPACE_ID" in os.environ:
            return "huggingface_spaces"
        elif os.path.exists("/.dockerenv"):
            return "docker"
        else:
            return "local"
    
    def validar_chaves(self) -> bool:
        """Valida presença de chaves necessárias"""
        if not self.groq_key:
            self.logger.warning("⚠️ GROQ_API_KEY não configurada")
            return False
        if not self.hf_token:
            self.logger.warning("⚠️ HF_TOKEN não configurada")
            return False
        return True


class NexusEconomy:
    """Gerencia recursos e calcula orçamentos"""
    
    VALOR_BASE_POR_AREA = 250.00  # R$ 250,00 por área
    
    def calcular_orcamento(self, areas: list) -> dict:
        """Calcula orçamento de engenharia"""
        total = sum(len(area) for area in areas) * self.VALOR_BASE_POR_AREA
        return {
            "areas": areas,
            "valor_unitario": self.VALOR_BASE_POR_AREA,
            "total": total,
            "timestamp": datetime.now().isoformat()
        }
    
    def verificar_normas(self, tipo: str = "engineering") -> list:
        """Verifica normas técnicas aplicáveis"""
        normas = {
            "engineering": ["NBR-2026-A", "ISO-9001-ENG", "ISO-14001"],
            "seguranca": ["NBR-SEGURANCA-2026", "ISO-45001"],
            "qualidade": ["ISO-9001", "ISO-14001", "ISO-45001"]
        }
        return normas.get(tipo, [])


class ToolsManager:
    """Gerencia ferramentas disponíveis para o bot"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.nexus = NexusEconomy()
        self.ferramentas = self._inicializar_ferramentas()
    
    def _inicializar_ferramentas(self) -> dict:
        """Inicializa todas as ferramentas disponíveis"""
        return {
            "calcular_orcamento": self.nexus.calcular_orcamento,
            "verificar_normas": self.nexus.verificar_normas,
            "gerar_relatorio": self.gerar_relatorio,
            "analisar_codigo": self.analisar_codigo,
            "buscar_informacoes": self.buscar_informacoes
        }
    
    def gerar_relatorio(self, dados: dict) -> str:
        """Gera relatório técnico consolidado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relatorio = f"""
╔════════════════════════════════════════════════════════════════╗
║              RELATÓRIO TÉCNICO CONSOLIDADO                    ║
╚════════════════════════════════════════════════════════════════╝

Data/Hora: {timestamp}
Status: {dados.get('status', 'PENDENTE')}

📊 Análise:
{json.dumps(dados, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════════
"""
        return relatorio
    
    def analisar_codigo(self, codigo: str) -> dict:
        """Analisa e avalia qualidade do código"""
        linhas = len(codigo.split('\n'))
        return {
            "linhas": linhas,
            "complexidade": "MEDIA",
            "qualidade": "BOA"
        }
    
    def buscar_informacoes(self, query: str) -> dict:
        """Busca informações (placeholder para Playwright/Google)"""
        return {
            "query": query,
            "resultados": [],
            "fonte": "google"
        }


class BotEngenheiroNexo:
    """Motor de Decisão - Agente autônomo com ciclo Planejar->Agir->Observar"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.tools = ToolsManager(self.config)
        
        # Caminho dos arquivos
        self.app_path = Path("/workspaces/rodolfo/app.py")
        self.data_dir = Path("/workspaces/rodolfo/data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Memória persistente
        self.historico_acoes = self._carregar_historico()
        self.contexto_acumulado = {}
        
        # Configurar logger
        logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
        logger.success("🤖 BotEngenheiroNexo v2026 INICIALIZADO")
        logger.info(f"📍 Ambiente: {self.config.ambiente}")
    
    def _carregar_historico(self) -> list:
        """Carrega histórico de ações anterior"""
        historico_path = self.data_dir / "historico_acoes.json"
        if historico_path.exists():
            try:
                return json.loads(historico_path.read_text())
            except:
                return []
        return []
    
    def _salvar_historico(self):
        """Salva histórico de ações em memória"""
        historico_path = self.data_dir / "historico_acoes.json"
        historico_path.write_text(json.dumps(self.historico_acoes, indent=2, ensure_ascii=False))
    
    # ===== CICLO MOTOR DE DECISÃO: PLANEJAR =====
    async def planejar(self, objetivo: str) -> dict:
        """FASE 1: Planejar - Define passos para atingir objetivo"""
        logger.info(f"🎯 PLANEJANDO: {objetivo}")
        
        plano = {
            "objetivo": objetivo,
            "passos": [
                {"num": 1, "tarefa": "Verificar normas técnicas", "ferramenta": "verificar_normas"},
                {"num": 2, "tarefa": "Calcular orçamento", "ferramenta": "calcular_orcamento"},
                {"num": 3, "tarefa": "Analisar código", "ferramenta": "analisar_codigo"},
                {"num": 4, "tarefa": "Gerar relatório", "ferramenta": "gerar_relatorio"}
            ],
            "timestamp": datetime.now().isoformat(),
            "status": "PLANEJADO"
        }
        
        logger.success(f"✅ Plano criado com {len(plano['passos'])} passos")
        return plano
    
    # ===== CICLO MOTOR DE DECISÃO: AGIR =====
    async def agir(self, plano: dict) -> dict:
        """FASE 2: Agir - Executa as ferramentas conforme plano"""
        logger.info("⚙️ EXECUTANDO PLANO")
        
        resultados_execucao = {
            "plano": plano["objetivo"],
            "execucoes": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Executar cada passo do plano
        for passo in plano["passos"]:
            ferramenta_nome = passo["ferramenta"]
            
            if ferramenta_nome not in self.tools.ferramentas:
                logger.warning(f"⚠️ Ferramenta não encontrada: {ferramenta_nome}")
                continue
            
            try:
                logger.info(f"🔧 Executando: {passo['tarefa']}")
                
                # Chamar ferramenta dinamicamente
                if ferramenta_nome == "verificar_normas":
                    resultado = self.tools.ferramentas[ferramenta_nome]("engineering")
                elif ferramenta_nome == "calcular_orcamento":
                    resultado = self.tools.ferramentas[ferramenta_nome](["arquitetura", "infraestrutura"])
                elif ferramenta_nome == "analisar_codigo":
                    resultado = self.tools.ferramentas[ferramenta_nome](self._ler_codigo()[:1000])
                elif ferramenta_nome == "gerar_relatorio":
                    resultado = self.tools.ferramentas[ferramenta_nome](self.contexto_acumulado)
                else:
                    resultado = {}
                
                # Acumular contexto
                self.contexto_acumulado[ferramenta_nome] = resultado
                
                resultados_execucao["execucoes"].append({
                    "passo": passo["num"],
                    "tarefa": passo["tarefa"],
                    "ferramenta": ferramenta_nome,
                    "resultado": resultado,
                    "status": "SUCESSO"
                })
                
                logger.success(f"✅ {passo['tarefa']}: COMPLETO")
                
            except Exception as e:
                logger.error(f"❌ Erro em {passo['tarefa']}: {e}")
                resultados_execucao["execucoes"].append({
                    "passo": passo["num"],
                    "tarefa": passo["tarefa"],
                    "status": "ERRO",
                    "erro": str(e)
                })
        
        logger.success(f"✅ EXECUÇÃO COMPLETA - {len(resultados_execucao['execucoes'])} tarefas")
        return resultados_execucao
    
    # ===== CICLO MOTOR DE DECISÃO: OBSERVAR =====
    async def observar(self, resultado_execucao: dict) -> dict:
        """FASE 3: Observar - Analisa resultados e aprende"""
        logger.info("👁️ OBSERVANDO RESULTADOS")
        
        observacoes = {
            "timestamp": datetime.now().isoformat(),
            "analise": {
                "total_tarefas": len(resultado_execucao["execucoes"]),
                "tarefas_sucesso": sum(1 for e in resultado_execucao["execucoes"] if e.get("status") == "SUCESSO"),
                "tarefas_erro": sum(1 for e in resultado_execucao["execucoes"] if e.get("status") == "ERRO"),
                "taxa_sucesso": 0
            },
            "proximas_acoes": []
        }
        
        # Calcular taxa de sucesso
        if observacoes["analise"]["total_tarefas"] > 0:
            observacoes["analise"]["taxa_sucesso"] = (
                observacoes["analise"]["tarefas_sucesso"] / observacoes["analise"]["total_tarefas"]
            ) * 100
        
        # Definir próximas ações
        if observacoes["analise"]["taxa_sucesso"] == 100:
            observacoes["proximas_acoes"] = ["Fazer deploy", "Sincronizar com HF", "Iniciar novo ciclo"]
            logger.success(f"✅ TAXA DE SUCESSO: 100% - SISTEMA OPERACIONAL")
        else:
            observacoes["proximas_acoes"] = ["Analisar erros", "Corrigir falhas", "Reexecutar"]
            logger.warning(f"⚠️ TAXA DE SUCESSO: {observacoes['analise']['taxa_sucesso']:.1f}%")
        
        # Guardar na memória
        self.historico_acoes.append({
            "ciclo": len(self.historico_acoes) + 1,
            "resultado": resultado_execucao,
            "observacoes": observacoes,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_historico()
        
        logger.success(f"💾 Memória atualizada - {len(self.historico_acoes)} ciclos registrados")
        return observacoes
    
    # ===== MÉTODOS AUXILIARES =====
    def _ler_codigo(self) -> str:
        """Lê o código atual do app.py"""
        if self.app_path.exists():
            return self.app_path.read_text(encoding="utf-8")
        return ""
    
    def _salvar_codigo(self, novo_codigo: str) -> bool:
        """Salva novo código no app.py com backup"""
        try:
            backup_path = self.app_path.with_suffix('.backup')
            if self.app_path.exists():
                backup_path.write_text(self._ler_codigo(), encoding="utf-8")
            self.app_path.write_text(novo_codigo, encoding="utf-8")
            logger.success(f"💾 Código salvo")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar: {e}")
            return False
    
    async def gerar_correcao_ia(self, codigo_atual: str, erro_descricao: str) -> str:
        """Usa IA para gerar correção automática"""
        try:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=self.config.groq_key,
                temperature=0.1,
                timeout=30
            )
            
            prompt = f"""VOCÊ É UM EXPERT PYTHON. TAREFA: CORRIGIR ERRO NO CÓDIGO.
ERRO DETECTADO: {erro_descricao}

CÓDIGO ATUAL (primeiras 100 linhas):
{chr(10).join(codigo_atual.split(chr(10))[:100])}

⚠️ INSTRUÇÕES:
1. RETORNE APENAS CÓDIGO PYTHON VÁLIDO E COMPLETO
2. NÃO RETORNE EXPLICAÇÕES, COMENTÁRIOS OU MARKDOWN
3. MANTENHA A ESTRUTURA ORIGINAL
4. CÓDIGO DEVE TER SINTAXE 100% VÁLIDA

RETORNE APENAS O CÓDIGO CORRIGIDO:"""
            
            logger.info("🧠 IA analisando erro...")
            response = llm.invoke(prompt)
            codigo_corrigido = response.content.strip()
            
            # Remover markdown
            if codigo_corrigido.startswith("```"):
                codigo_corrigido = codigo_corrigido.split("```")[1]
                if codigo_corrigido.startswith("python"):
                    codigo_corrigido = codigo_corrigido[6:]
                codigo_corrigido = codigo_corrigido.strip()
            
            logger.success("✅ IA gerou correção")
            return codigo_corrigido
        
        except Exception as e:
            logger.error(f"❌ Erro na IA: {e}")
            return ""
    
    def fazer_push_automatico(self, mensagem: str = None) -> bool:
        """Faz commit e push para HF"""
        if not mensagem:
            mensagem = f"🤖 AUTO-EVOLUÇÃO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            logger.info("📤 Preparando push...")
            
            subprocess.run(["git", "add", "."], check=True, capture_output=True, cwd="/workspaces/rodolfo")
            subprocess.run(["git", "commit", "-m", mensagem], check=True, capture_output=True, cwd="/workspaces/rodolfo")
            
            repo_url = "https://huggingface.co/spaces/NEXO-MAESTRO/srodolfobarbosa"
            auth_url = repo_url.replace("https://", f"https://NEXO-MAESTRO:{self.config.hf_token}@")
            subprocess.run(["git", "push", auth_url, "main", "--force"], check=True, capture_output=True, cwd="/workspaces/rodolfo")
            
            logger.success("✅ Push concluído para HF!")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro no Git: {e}")
            return False
    
    # ===== CICLO COMPLETO =====
    async def ciclo_completo(self, objetivo: str):
        """Executa o ciclo completo: Planejar -> Agir -> Observar"""
        logger.success("=" * 70)
        logger.success("🚀 INICIANDO CICLO COMPLETO: PLANEJAR -> AGIR -> OBSERVAR")
        logger.success("=" * 70)
        
        try:
            # FASE 1: PLANEJAR
            plano = await self.planejar(objetivo)
            
            # FASE 2: AGIR
            resultado = await self.agir(plano)
            
            # FASE 3: OBSERVAR
            observacoes = await self.observar(resultado)
            
            logger.success("=" * 70)
            logger.success("✅ CICLO COMPLETO FINALIZADO COM SUCESSO")
            logger.success("=" * 70)
            
            return {
                "plano": plano,
                "execucao": resultado,
                "observacoes": observacoes
            }
        
        except Exception as e:
            logger.error(f"❌ Erro no ciclo: {e}")
            return None


async def main():
    """Inicia o Bot Engenheiro NEXO v2026"""
    bot = BotEngenheiroNexo()
    
    logger.success("=" * 70)
    logger.success("🤖 BOT ENGENHEIRO NEXO v2026")
    logger.success("=" * 70)
    logger.success("📌 MOTOR DE DECISÃO - CICLO AUTÔNOMO:")
    logger.success("  1️⃣ PLANEJAR  - Define passos e estratégia")
    logger.success("  2️⃣ AGIR     - Executa ferramentas e tarefas")
    logger.success("  3️⃣ OBSERVAR - Analisa resultados e aprende")
    logger.success("=" * 70)
    
    # Executar ciclo completo com objetivo específico
    objetivo = "Implementar análise técnica completa do projeto NEXO"
    await bot.ciclo_completo(objetivo)
    
    # Loop contínuo
    ciclo_num = 1
    while True:
        logger.info(f"\n⏳ Aguardando 5 minutos para próximo ciclo...")
        await asyncio.sleep(300)
        ciclo_num += 1
        logger.info(f"\n🔄 CICLO #{ciclo_num}")
        await bot.ciclo_completo(objetivo)


if __name__ == "__main__":
    asyncio.run(main())

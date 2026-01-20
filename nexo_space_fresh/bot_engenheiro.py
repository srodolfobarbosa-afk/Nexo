#!/usr/bin/env python3
"""
🤖 BOT ENGENHEIRO NEXO - SISTEMA AUTÔNOMO INTELIGENTE
Auto-detecta, corrige, reconstrói e faz auto-deploy para Hugging Face
Objetivo: Criar um agente IA que entende seu próprio código e evolui automaticamente
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

class BotEngenheiroNexo:
    """Agente autônomo que evolui o próprio código e se auto-implanta"""
    
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.hf_token = os.getenv("HF_TOKEN")
        self.email = "srodolfo@gmail.com"
        self.username = "NEXO-MAESTRO"
        self.repo_url = "https://huggingface.co/spaces/NEXO-MAESTRO/srodolfobarbosa"
        self.app_path = Path("/workspaces/rodolfo/app.py")
        self.errors_log = Path("/workspaces/rodolfo/data/evolucao.json")
        self.errors_log.parent.mkdir(exist_ok=True)
        
        logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
        logger.success("🤖 BotEngenheiroNexo: INICIALIZADO - OBJETIVO: AUTO-EVOLUÇÃO E AUTO-DEPLOY")
    
    def ler_codigo(self) -> str:
        """Lê o código atual do app.py"""
        if self.app_path.exists():
            return self.app_path.read_text(encoding="utf-8")
        return ""
    
    def salvar_codigo(self, novo_codigo: str) -> bool:
        """Salva novo código no app.py com backup"""
        try:
            # Backup do código anterior
            backup_path = self.app_path.with_suffix('.backup')
            if self.app_path.exists():
                backup_path.write_text(self.app_path.read_text(encoding="utf-8"), encoding="utf-8")
            
            self.app_path.write_text(novo_codigo, encoding="utf-8")
            logger.success(f"💾 Código salvo: {self.app_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar código: {e}")
            return False
    
    def registrar_evolucao(self, tipo: str, descricao: str, sucesso: bool):
        """Registra evolução no log"""
        evolucao = {
            "timestamp": datetime.now().isoformat(),
            "tipo": tipo,
            "descricao": descricao,
            "sucesso": sucesso
        }
        
        try:
            if self.errors_log.exists():
                logs = json.loads(self.errors_log.read_text())
            else:
                logs = []
            
            logs.append(evolucao)
            self.errors_log.write_text(json.dumps(logs, indent=2))
            logger.info(f"📝 Evolução registrada: {tipo} - {descricao}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao registrar evolução: {e}")
    
    def analisar_erros(self) -> list:
        """Analisa erros recentes do sistema"""
        try:
            memoria_path = Path("/workspaces/rodolfo/data/memoria_soberana.json")
            if memoria_path.exists():
                memoria = json.loads(memoria_path.read_text())
                erros = memoria.get("erros", [])
                return erros[-10:]  # Últimos 10 erros
        except:
            pass
        return []
    
    async def entender_objetivo(self, codigo: str = None) -> dict:
        """IA analisa o código e entende o objetivo do sistema"""
        try:
            if not codigo:
                codigo = self.ler_codigo()[:3000]
            
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=self.groq_key,
                temperature=0.2,
                timeout=30
            )
            
            prompt = f"""Analise este código Python e responda em JSON:

CÓDIGO:
{codigo}

Responda APENAS em JSON (sem explicações) com esta estrutura:
{{
    "objetivo": "Descrição breve do objetivo",
    "funcionalidades": ["lista", "de", "funcionalidades"],
    "proximas_evolucoes": ["sugestão1", "sugestão2"],
    "status": "OPERACIONAL|ERRO|IMPLEMENTAÇÃO"
}}"""
            
            response = llm.invoke(prompt)
            # Extrai JSON da resposta
            texto = response.content
            inicio = texto.find('{')
            fim = texto.rfind('}') + 1
            
            if inicio >= 0 and fim > inicio:
                json_str = texto[inicio:fim]
                resultado = json.loads(json_str)
                logger.info(f"🎯 Objetivo identificado: {resultado.get('objetivo')}")
                return resultado
            else:
                logger.warning("⚠️ Não consegui extrair JSON da resposta")
                return {}
        
        except Exception as e:
            logger.error(f"❌ Erro ao entender objetivo: {e}")
            return {}
    
    async def gerar_correcao_ia(self, codigo_atual: str, erro_descricao: str) -> str:
        """Usa IA para gerar correção automática inteligente"""
        try:
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=self.groq_key,
                temperature=0.1,  # Mais baixo para código mais preciso
                timeout=30
            )
            
            # Limpar o código para melhor análise
            linhas = codigo_atual.split('\n')
            
            prompt = f"""VOCÊ É UM EXPERT PYTHON. TAREFA: CORRIGIR ERRO NO CÓDIGO.

ERRO DETECTADO: {erro_descricao}

CÓDIGO ATUAL (linhas 1-100):
{chr(10).join(linhas[:100])}

⚠️ INSTRUÇÕES CRÍTICAS:
1. RETORNE APENAS CÓDIGO PYTHON VÁLIDO E COMPLETO
2. NÃO RETORNE EXPLICAÇÕES, COMENTÁRIOS OU MARKDOWN
3. MANTENHA A ESTRUTURA E FUNCIONALIDADE ORIGINAL
4. ADICIONE TRATAMENTO DE ERRO SE NECESSÁRIO
5. CÓDIGO DEVE TER SINTAXE 100% VÁLIDA
6. Comece com imports, termina com a função main

RETORNE APENAS O CÓDIGO CORRIGIDO:"""
            
            logger.info("🧠 IA analisando erro e gerando correção...")
            response = llm.invoke(prompt)
            codigo_corrigido = response.content.strip()
            
            # Remover markdown code blocks se existirem
            if codigo_corrigido.startswith("```python"):
                codigo_corrigido = codigo_corrigido[9:]
            if codigo_corrigido.startswith("```"):
                codigo_corrigido = codigo_corrigido[3:]
            if codigo_corrigido.endswith("```"):
                codigo_corrigido = codigo_corrigido[:-3]
            
            codigo_corrigido = codigo_corrigido.strip()
            
            # Validação básica
            if len(codigo_corrigido) > 300 and "import" in codigo_corrigido:
                logger.success("✅ IA gerou correção válida")
                return codigo_corrigido
            else:
                logger.warning("⚠️ IA retornou código muito curto ou inválido")
                return ""
        
        except Exception as e:
            logger.error(f"❌ Erro na IA: {e}")
            return ""
    
    def testar_sintaxe(self, codigo: str) -> bool:
        """Testa se o código tem sintaxe válida"""
        try:
            compile(codigo, '<string>', 'exec')
            logger.success("✅ Sintaxe validada com sucesso")
            return True
        except SyntaxError as e:
            logger.error(f"❌ Erro de sintaxe: {e}")
            return False
    
    async def auto_corrigir(self, erro_tipo: str, erro_msg: str) -> bool:
        """Executa ciclo completo de auto-correção"""
        logger.warning(f"🔧 Iniciando auto-correção para: {erro_tipo}")
        
        # 1. Ler código
        codigo_atual = self.ler_codigo()
        if not codigo_atual:
            logger.error("❌ Não consegui ler o código atual")
            return False
        
        # 2. IA gera correção
        codigo_novo = await self.gerar_correcao_ia(codigo_atual, f"{erro_tipo}: {erro_msg}")
        if not codigo_novo:
            logger.error("❌ IA não conseguiu gerar correção")
            self.registrar_evolucao("AUTO_CORRECAO", erro_tipo, False)
            return False
        
        # 3. Testar sintaxe
        if not self.testar_sintaxe(codigo_novo):
            logger.error("❌ Código corrigido tem erro de sintaxe")
            self.registrar_evolucao("AUTO_CORRECAO", f"{erro_tipo} - Sintaxe inválida", False)
            return False
        
        # 4. Salvar
        if not self.salvar_codigo(codigo_novo):
            logger.error("❌ Não consegui salvar o código")
            return False
        
        # 5. Registrar evolução
        self.registrar_evolucao("AUTO_CORRECAO", erro_tipo, True)
        logger.success(f"✅ Auto-correção completa para: {erro_tipo}")
        
        return True
    
    def configurar_git(self) -> bool:
        """Configura credenciais Git"""
        try:
            subprocess.run(
                ["git", "config", "--global", "user.email", self.email],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "--global", "user.name", self.username],
                check=True,
                capture_output=True
            )
            logger.success("✅ Git configurado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Git: {e}")
            return False
    
    def fazer_push_automatico(self, mensagem: str = None) -> bool:
        """Faz commit e push automático para Hugging Face"""
        if not mensagem:
            mensagem = f"🤖 AUTO-EVOLUÇÃO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            logger.info("📤 Preparando push automático...")
            
            # 1. Git add
            subprocess.run(["git", "add", "."], check=True, capture_output=True, cwd="/workspaces/rodolfo")
            logger.success("✅ Arquivos adicionados")
            
            # 2. Git commit
            subprocess.run(
                ["git", "commit", "-m", mensagem],
                check=True,
                capture_output=True,
                cwd="/workspaces/rodolfo"
            )
            logger.success("✅ Commit realizado")
            
            # 3. Git push
            auth_url = self.repo_url.replace("https://", f"https://{self.username}:{self.hf_token}@")
            subprocess.run(
                ["git", "push", auth_url, "main", "--force"],
                check=True,
                capture_output=True,
                cwd="/workspaces/rodolfo"
            )
            logger.success("✅ Push concluído para Hugging Face!")
            self.registrar_evolucao("GIT_PUSH", mensagem, True)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro no Git: {e}")
            self.registrar_evolucao("GIT_PUSH", f"Erro: {str(e)}", False)
            return False
    
    async def ciclo_autonomo(self):
        """Loop autônomo de monitoramento e evolução"""
        logger.success("🚀 CICLO AUTÔNOMO INICIADO - SISTEMA EVOLUINDO CONTINUAMENTE")
        logger.success("🔄 PROCESSO: Detectar → Corrigir → Validar → Deploy HF")
        logger.success("=" * 70)
        
        ciclo = 0
        while True:
            ciclo += 1
            try:
                logger.info(f"\n🔄 CICLO #{ciclo} - Verificando sistema...")
                
                # 1. Entender objetivo (a cada 5 ciclos)
                if ciclo % 5 == 0:
                    objetivo = await self.entender_objetivo()
                    if objetivo:
                        logger.info(f"📌 OBJETIVO: {objetivo.get('objetivo', 'N/A')}")
                        logger.info(f"🔄 PROCESSO: Detectar → Corrigir → Validar → Deploy HF")
                
                # 2. Analisar erros
                erros = self.analisar_erros()
                
                if erros:
                    erro_recente = erros[-1]
                    tipo_erro = erro_recente.get('type', 'DESCONHECIDO')
                    logger.warning(f"⚠️ Erro detectado: {tipo_erro}")
                    
                    # 3. Auto-corrigir
                    sucesso = await self.auto_corrigir(
                        tipo_erro,
                        erro_recente.get('details', '')
                    )
                    
                    if sucesso:
                        # 4. Fazer push
                        logger.info("📤 Preparando sincronização com repositório...")
                        if self.configurar_git():
                            self.fazer_push_automatico(f"🧬 Auto-correção: {tipo_erro}")
                        
                        # 5. Aguardar um pouco antes de próximo ciclo
                        logger.info("⏳ Aguardando 10s antes de próximo ciclo...")
                        await asyncio.sleep(10)
                else:
                    logger.info("✨ Nenhum erro detectado. Sistema operacional normal.")
                
                # Ciclo a cada 5 minutos
                logger.info("⏳ Próximo ciclo em 5 minutos...")
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ Erro no ciclo autônomo: {e}")
                await asyncio.sleep(60)


async def main():
    """Inicia o Bot Engenheiro - Sistema Autônomo"""
    bot = BotEngenheiroNexo()
    
    logger.success("=" * 70)
    logger.success("🤖 BOT ENGENHEIRO NEXO - SISTEMA COMPLETAMENTE AUTÔNOMO")
    logger.success("=" * 70)
    logger.success("📌 FUNCIONALIDADES:")
    logger.success("  ✅ Chat com LLM (GROQ/Llama)")
    logger.success("  ✅ Detecta erros automaticamente")
    logger.success("  ✅ Corrige código com IA")
    logger.success("  ✅ Auto-valida sintaxe")
    logger.success("  ✅ Faz auto-deploy para Hugging Face")
    logger.success("  ✅ Sincroniza automaticamente")
    logger.success("  ✅ Evolui continuamente")
    logger.success("=" * 70)
    
    # Inicia ciclo autônomo
    await bot.ciclo_autonomo()


if __name__ == "__main__":
    asyncio.run(main())

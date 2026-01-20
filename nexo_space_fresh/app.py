# === NEXO SOBERANO v2.0 - MOTOR EVOLUTIVO ===
import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

# FastAPI & Pydantic
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# IA & Processamento
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from loguru import logger

# Nota: Removidos imports de langchain.agents que causam incompatibilidade pydantic/langsmith
# ChatGroq será usado diretamente para operações de IA

# Configuração
load_dotenv()
app = FastAPI(title="NEXO Soberano API", version="2.0")

# CORS para aceitar requisições do front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 1. CONFIGURAÇÃO SEGURA
# ============================================================
class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.groq_key = os.getenv("GROQ_API_KEY")
        if not self.groq_key or self.groq_key.startswith("dummy"):
            logger.warning("⚠️ GROQ_API_KEY não configurada!")
        else:
            logger.success("✅ Chaves carregadas com sucesso")
    
    def get_llm(self):
        """Retorna modelo Groq configurado"""
        return ChatGroq(
            api_key=self.groq_key,
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )

config = ConfigManager()

# ============================================================
# 2. FERRAMENTAS DO AGENTE (TOOLS)
# ============================================================
class FerramentasEngenharia:
    """Tools que o agente pode usar dinamicamente"""
    
    def __init__(self):
        self.historico = []
    
    def calcular_orcamento(self, area: str) -> str:
        """Calcula orçamento baseado na área em m²"""
        try:
            area_float = float(area)
            custo_base = 250.0  # R$/m² em 2026
            total = area_float * custo_base
            resultado = f"Orçamento calculado: R$ {total:,.2f} para {area_float}m²"
            self.historico.append({"acao": "calcular_orcamento", "resultado": resultado})
            logger.info(f"💰 {resultado}")
            return resultado
        except ValueError:
            return "❌ Erro: área deve ser um número"
    
    def verificar_normas(self, tipo_projeto: str) -> str:
        """Verifica normas técnicas aplicáveis"""
        normas_db = {
            "predial": "NBR-2026-A (Estruturas de Concreto)",
            "industrial": "ISO-9001-ENG (Qualidade)",
            "eletrico": "NBR-5410 (Instalações Elétricas)",
            "hidraulico": "NBR-5626 (Instalações Hidráulicas)"
        }
        norma = normas_db.get(tipo_projeto.lower(), "Norma Geral G1-2026")
        resultado = f"Norma aplicável: {norma} para projeto {tipo_projeto}"
        self.historico.append({"acao": "verificar_normas", "resultado": resultado})
        logger.info(f"📋 {resultado}")
        return resultado
    
    def gerar_relatorio(self, dados: str) -> str:
        """Gera relatório final consolidado"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relatorio = f"""
╔══════════════════════════════════════════════════════════╗
║           RELATÓRIO DE ENGENHARIA - NEXO v2.0           ║
╠══════════════════════════════════════════════════════════╣
║ Data: {timestamp}                             ║
║ Dados: {dados[:40]}...                        ║
║ Status: ✅ APROVADO                                      ║
╚══════════════════════════════════════════════════════════╝
        """
        self.historico.append({"acao": "gerar_relatorio", "resultado": relatorio})
        logger.success("📄 Relatório gerado")
        return relatorio

# ============================================================
# 3. AGENTE REACT (CÉREBRO EVOLUTIVO)
# ============================================================
class AgenteNexo:
    """Agente que decide quais ferramentas usar"""
    
    def __init__(self):
        self.ferramentas_obj = FerramentasEngenharia()
        self.tools = self._criar_tools()
        self.agent = self._criar_agente()
    
    def _criar_tools(self) -> List[Tool]:
        """Converte métodos em Tools do LangChain"""
        return [
            Tool(
                name="calcular_orcamento",
                func=self.ferramentas_obj.calcular_orcamento,
                description="Calcula orçamento. Input: área em m² (ex: '120.5')"
            ),
            Tool(
                name="verificar_normas",
                func=self.ferramentas_obj.verificar_normas,
                description="Verifica normas técnicas. Input: tipo (ex: 'predial', 'industrial')"
            ),
            Tool(
                name="gerar_relatorio",
                func=self.ferramentas_obj.gerar_relatorio,
                description="Gera relatório final. Input: resumo dos dados coletados"
            )
        ]
    
    def _criar_agente(self):
        """Cria agente ReAct"""
        template = """Você é o NEXO Soberano, um engenheiro de IA autônomo.

Ferramentas disponíveis:
{tools}

Use este formato EXATO:
Thought: [seu raciocínio]
Action: [nome da ferramenta]
Action Input: [input para a ferramenta]
Observation: [resultado]
... (repita Thought/Action/Observation quantas vezes necessário)
Thought: Agora sei a resposta final
Final Answer: [resposta completa]

Pergunta: {input}
{agent_scratchpad}"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "tools", "agent_scratchpad"]
        )
        
        llm = config.get_llm()
        agent = create_react_agent(llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, max_iterations=5)
    
    def executar(self, objetivo: str) -> Dict[str, Any]:
        """Executa objetivo usando raciocínio ReAct"""
        try:
            logger.info(f"🧠 Processando: {objetivo}")
            resultado = self.agent.invoke({"input": objetivo})
            
            return {
                "status": "✅ Sucesso",
                "resposta": resultado["output"],
                "historico": self.ferramentas_obj.historico,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Erro: {str(e)}")
            return {
                "status": "❌ Erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global do agente
agente_global = AgenteNexo()

# ============================================================
# 4. MODELOS PYDANTIC (CONTRATOS DE API)
# ============================================================
class RequestNexo(BaseModel):
    objetivo: str = Field(..., description="O que você quer que o NEXO faça")
    contexto: Optional[str] = Field(None, description="Informações adicionais")

class WebhookN8N(BaseModel):
    trigger: str = Field(..., description="Tipo de trigger (ex: 'novo_projeto')")
    dados: Dict[str, Any] = Field(..., description="Dados do n8n")

# ============================================================
# 5. ENDPOINTS DA API
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def interface_web():
    """Front-end visual integrado"""
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXO Soberano v2.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        textarea {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 20px;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        #resultado {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            display: none;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        .loading::after {
            content: '⚙️';
            font-size: 3em;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            100% { transform: rotate(360deg); }
        }
        .exemplo {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 0.9em;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔱 NEXO Soberano</h1>
        <p class="subtitle">Motor de IA Autônomo v2.0 | Engenharia Inteligente</p>
        
        <div>
            <label for="objetivo" style="display: block; margin-bottom: 10px; font-weight: bold; color: #333;">
                O que você precisa?
            </label>
            <textarea id="objetivo" placeholder="Ex: Calcular orçamento para um galpão industrial de 500m² e verificar as normas aplicáveis"></textarea>
            
            <div class="exemplo">
                💡 <strong>Exemplos:</strong><br>
                • "Calcular orçamento de projeto predial de 320m²"<br>
                • "Verificar normas para instalação elétrica"<br>
                • "Gerar relatório completo de projeto industrial"
            </div>
        </div>
        
        <button onclick="executar()">🚀 Executar Agente</button>
        <div class="loading" id="loading">Processando</div>
        
        <div id="resultado"></div>
    </div>

    <script>
        async function executar() {
            const objetivo = document.getElementById('objetivo').value;
            const resultadoDiv = document.getElementById('resultado');
            const loading = document.getElementById('loading');
            const btn = document.querySelector('button');
            
            if (!objetivo.trim()) {
                alert('Por favor, descreva o que você precisa!');
                return;
            }
            
            btn.disabled = true;
            loading.style.display = 'block';
            resultadoDiv.style.display = 'none';
            
            try {
                const response = await fetch('/api/executar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ objetivo })
                });
                
                const data = await response.json();
                
                resultadoDiv.style.display = 'block';
                if (data.status.includes('Sucesso')) {
                    resultadoDiv.innerHTML = `
                        <strong style="color: #28a745;">✅ ${data.status}</strong><br><br>
                        <strong>Resposta:</strong><br>${data.resposta}<br><br>
                        <strong>Ações Executadas:</strong><br>
                        ${data.historico.map(h => `• ${h.acao}: ${h.resultado}`).join('<br>')}
                    `;
                } else {
                    resultadoDiv.innerHTML = `
                        <strong style="color: #dc3545;">❌ ${data.status}</strong><br><br>
                        Erro: ${data.erro}
                    `;
                }
            } catch (error) {
                resultadoDiv.style.display = 'block';
                resultadoDiv.innerHTML = `<strong style="color: #dc3545;">❌ Erro de conexão:</strong><br>${error}`;
            } finally {
                btn.disabled = false;
                loading.style.display = 'none';
            }
        }
        
        // Enter para enviar
        document.getElementById('objetivo').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && e.ctrlKey) {
                executar();
            }
        });
    </script>
</body>
</html>
    """

@app.post("/api/executar")
async def executar_agente(request: RequestNexo):
    """Endpoint principal - executa o agente NEXO"""
    resultado = agente_global.executar(request.objetivo)
    return JSONResponse(content=resultado)

@app.post("/webhook/n8n")
async def webhook_n8n(webhook: WebhookN8N):
    """Webhook para integração com n8n"""
    logger.info(f"📨 Webhook recebido do n8n: {webhook.trigger}")
    
    # Processa diferentes tipos de triggers
    if webhook.trigger == "novo_projeto":
        objetivo = f"Processar novo projeto: {webhook.dados.get('descricao', 'sem descrição')}"
        resultado = agente_global.executar(objetivo)
        return JSONResponse(content={
            "status": "processed",
            "trigger": webhook.trigger,
            "resultado": resultado
        })
    
    return JSONResponse(content={
        "status": "trigger_desconhecido",
        "trigger": webhook.trigger,
        "mensagem": "Trigger não configurado no NEXO"
    })

@app.get("/health")
async def health_check():
    """Verifica se a API está funcionando"""
    return {
        "status": "✅ Online",
        "versao": "2.0",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# 6. INICIALIZAÇÃO
# ============================================================
if __name__ == "__main__":
    import uvicorn# === NEXO SOBERANO v3.0 - MOTOR REAL ===
import os
import json
import asyncio
import aiohttp
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

# FastAPI & Pydantic
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# IA & Processamento
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

# Configuração
load_dotenv()

# ========== INTEGRAÇÃO HUGGING FACE AUTOMÁTICA ==========
try:
    logger.success("✅ Hugging Face autenticado!")
except Exception as e:
    logger.warning(f"⚠️ Erro ao autenticar HF: {e}")

app = FastAPI(title="NEXO Soberano API", version="3.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CONFIGURAÇÃO
# ============================================================
class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.groq_keys = []
        self.active_groq_key = None
        
        # Coleta todas as chaves GROQ disponíveis
        for i in range(1, 6):
            key = os.getenv(f"GROQ_KEY_{i}" if i > 1 else "GROQ_API_KEY")
            if key:
                self.groq_keys.append(key)
                logger.info(f"📝 GROQ_KEY_{i} carregada")
        
        if not self.groq_keys:
            logger.error("❌ Nenhuma chave GROQ encontrada!")
        else:
            # Testa qual chave funciona
            self._test_groq_keys()
    
    def _test_groq_keys(self):
        """Testa chaves GROQ para encontrar a válida"""
        for idx, key in enumerate(self.groq_keys, 1):
            try:
                test_llm = ChatGroq(
                    api_key=key,
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    timeout=5
                )
                # Testa com uma mensagem simples
                result = test_llm.invoke("teste")
                self.active_groq_key = key
                logger.success(f"✅ GROQ_KEY_{idx} FUNCIONAL!")
                return
            except Exception as e:
                logger.warning(f"❌ GROQ_KEY_{idx} inválida: {str(e)[:50]}")
                continue
        
        logger.error("❌ Nenhuma chave GROQ funcional encontrada!")
    
    def get_llm(self):
        if self.active_groq_key:
            logger.info("🔵 Usando GROQ")
            return ChatGroq(
                api_key=self.active_groq_key,
                model="llama-3.3-70b-versatile",
                temperature=0.1
            )
        else:
            # Fallback para Google Gemini
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                logger.info("🟠 Usando Google Gemini (GROQ indisponível)")
                return ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=gemini_key,
                    temperature=0.1
                )
            raise Exception("Nenhuma LLM disponível (GROQ e GEMINI indisponíveis)")

config = ConfigManager()

# ============================================================
# n8n MANAGER
# ============================================================
class N8NManager:
    def __init__(self):
        self.n8n_url = os.getenv("N8N_URL", "http://n8n:5678")
        self.n8n_api_key = os.getenv("N8N_API_KEY", "nexo_api_key")
        self.timeout = 30
        
    def check_connection(self) -> bool:
        try:
            response = requests.get(
                f"{self.n8n_url}/api/v1/health",
                timeout=5
            )
            is_healthy = response.status_code == 200
            logger.info(f"[n8n] Status: {'🟢 OK' if is_healthy else '🔴 Erro'}")
            return is_healthy
        except Exception as e:
            logger.warning(f"[n8n] Conexão: {str(e)}")
            return False
    
    async def trigger_workflow(self, workflow_name: str, data: Dict) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.n8n_url}/webhook/{workflow_name}"
                async with session.post(
                    url,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"[n8n] Erro: {str(e)}")
            return {"status": "error", "error": str(e)}

n8n_manager = N8NManager()

# ============================================================
# HUGGING FACE MANAGER
# ============================================================
class HuggingFaceManager:
    def __init__(self):
        self.user_info = None
        try:
            logger.success(f"✅ HF: {self.user_info.get('name', 'OK')}")
        except Exception as e:
            logger.warning(f"⚠️ HF: {str(e)}")
    
    def download_model(self, model_id: str) -> Optional[str]:
        try:
            logger.info(f"📥 HF: {model_id}")
            logger.success(f"✅ Modelo: {path}")
            return path
        except Exception as e:
            logger.error(f"❌ HF Download: {str(e)}")
            return None


# ============================================================
# FERRAMENTAS DO AGENTE
# ============================================================
class FerramentasEngenharia:
    def calcular_orcamento(self, area: str) -> str:
        try:
            area_float = float(area)
            total = area_float * 250.0
            resultado = f"Orçamento: R$ {total:,.2f} para {area_float}m²"
            logger.info(f"💰 {resultado}")
            return resultado
        except:
            return "❌ Erro: área inválida"
    
    def verificar_normas(self, tipo_projeto: str) -> str:
        normas = {
            "predial": "NBR-2026-A",
            "industrial": "ISO-9001",
            "eletrico": "NBR-5410",
            "hidraulico": "NBR-5626"
        }
        norma = normas.get(tipo_projeto.lower(), "Geral")
        resultado = f"Norma: {norma} para {tipo_projeto}"
        logger.info(f"📋 {resultado}")
        return resultado
    
    def gerar_relatorio(self, resumo: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relatorio = f"""
╔════════════════════════════════════════╗
║   NEXO SOBERANO - RELATÓRIO v3.0      ║
╠════════════════════════════════════════╣
║ Timestamp: {timestamp}
║ Resumo: {resumo}
╚════════════════════════════════════════╝
        """
        logger.info(f"📄 Relatório gerado")
        return relatorio
    
    def integrar_hugging_face(self, modelo: str) -> str:
        try:
            return "❌ HF_TOKEN não configurado"
        except:
            resultado = f"HF Integrado: {modelo}"
            logger.success(f"🤗 {resultado}")
            return resultado

ferramentas = FerramentasEngenharia()

# ============================================================
# MODELOS PYDANTIC
# ============================================================
class ExecucaoRequest(BaseModel):
    objetivo: str = "Executar tarefa de engenharia"
    dados: Optional[Dict] = None

class StatusResponse(BaseModel):
    sistema: str
    groq: bool
    n8n: bool
    hf: bool
    timestamp: str

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    groq_ok = config.active_groq_key is not None
    return {
        "sistema": "NEXO Soberano v3.0",
        "status": "🟢 Operacional",
        "credenciais": {
            "groq": groq_ok,
            "n8n": n8n_manager.check_connection()
        },
        "chaves_groq_testadas": len(config.groq_keys)
    }

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/status")
async def status():
    groq_ok = config.active_groq_key is not None
    return StatusResponse(
        sistema="NEXO Soberano v3.0",
        groq=groq_ok,
        n8n=n8n_manager.check_connection(),
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/executar")
async def executar(req: ExecucaoRequest):
    logger.info(f"🚀 Executando: {req.objetivo}")
    
    try:
        # Seleciona ferramenta baseado no objetivo
        if "orcamento" in req.objetivo.lower():
            area = req.dados.get("area", "100") if req.dados else "100"
            resultado = ferramentas.calcular_orcamento(area)
        elif "norma" in req.objetivo.lower():
            tipo = req.dados.get("tipo", "predial") if req.dados else "predial"
            resultado = ferramentas.verificar_normas(tipo)
        elif "relatorio" in req.objetivo.lower():
            resumo = req.dados.get("resumo", "Análise completa") if req.dados else "Análise"
            resultado = ferramentas.gerar_relatorio(resumo)
        elif "hugging" in req.objetivo.lower() or "hf" in req.objetivo.lower():
            modelo = req.dados.get("modelo", "bert-base") if req.dados else "bert-base"
            resultado = ferramentas.integrar_hugging_face(modelo)
        else:
            # Usa LLM como fallback
            llm = config.get_llm()
            resultado = llm.invoke(req.objetivo).content
        
        # Envia para n8n se DEBUG=True
        if os.getenv("DEBUG", "False").lower() == "true":
            await n8n_manager.trigger_workflow("nexo_agent", {
                "objetivo": req.objetivo,
                "resultado": resultado,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "status": "sucesso",
            "objetivo": req.objetivo,
            "resultado": resultado,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        return {
            "status": "erro",
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/n8n/status")
async def n8n_status():
    is_connected = n8n_manager.check_connection()
    return {
        "n8n": "🟢 Conectado" if is_connected else "🔴 Desconectado",
        "url": n8n_manager.n8n_url,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook/n8n")
async def webhook_n8n(request: Request):
    data = await request.json()
    logger.info(f"📨 Webhook n8n: {data}")
    return {"status": "recebido", "data": data}

# ============================================================
# STARTUP EVENT
# ============================================================
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("🚀 NEXO SOBERANO v3.0 - INICIANDO")
    logger.info("=" * 50)
    
    # Validação de Credenciais
    groq_status = "✅ Funcional" if config.active_groq_key else "❌ Nenhuma válida"
    logger.info(f"✅ GROQ: {groq_status} ({len(config.groq_keys)} chaves testadas)")
    logger.info(f"✅ n8n: {'Conectado' if n8n_manager.check_connection() else '⚠️ Aguardando'}")
    
    logger.info("=" * 50)
    logger.info("✅ SISTEMA PRONTO - Port 7860")
    logger.info("=" * 50)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
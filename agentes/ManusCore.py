"""ManusCore - Agente núcleo responsável pela transição de Manus para residente no EcoGuardians.

Este agente é um scaffold operacional que contém rotinas para:
- coletar e exportar conhecimento
- gerar um plano técnico de migração
- executar rotinas diárias de aprendizado e monitoramento
- interfaces com EcoMemory e LLMProvider

É um ponto de partida para automatizar a transição descrita em MANUS_ACTIONS.md
"""
import os
import json
import time
from typing import Dict, Any, List, Optional

from core.memory import EcoMemory
from agentes.llm_provider import LLMProvider
from core.toolbelt import get_default_toolbelt


class ManusCore:
    """Scaffold do agente Manus residente.

    Métodos principais:
    - collect_knowledge(): agrega documentos e memórias relevantes
    - export_knowledge(path): salva bundle para migração
    - plan_migration(): gera um plano técnico (usa LLMProvider se disponível)
    - run_daily_cycle(): rotina diária: metrics -> learn -> report
    - monitor_and_heal(): detecta anomalias e sugere ações
    """

    def __init__(self, memory: Optional[EcoMemory] = None, llm: Optional[LLMProvider] = None):
        self.memory = memory or EcoMemory()
        self.llm = llm or LLMProvider()
        self.toolbelt = get_default_toolbelt()
        self.identity = {
            "name": "ManusCore",
            "version": "0.1",
            "owner": os.environ.get("OWNER", "Rodolfo"),
        }

    def collect_knowledge(self, include_docs: bool = True, recent_limit: int = 200) -> Dict[str, Any]:
        """Agrega memórias e arquivos relevantes do repositório para análise."""
        # coletar memórias recentes
        mems = self.memory.query_recent(limit=recent_limit)
        bundle = {"memories": mems}

        if include_docs:
            docs = {}
            # arquivos de documentação padrão
            candidates = ["BUSINESS_PLAN.md", "MANUS_ACTIONS.md", "PROJECT_CANVAS.md", "INFRASTRUCTURE_MAP.md"]
            for c in candidates:
                try:
                    with open(os.path.join(os.path.dirname(__file__), "..", c), encoding="utf-8") as f:
                        docs[c] = f.read()
                except Exception:
                    docs[c] = None
            bundle["docs"] = docs

        return bundle

    def export_knowledge(self, out_path: str = "manus_export.json") -> str:
        """Exporta o bundle de conhecimento para um arquivo JSON (pronto para transferir)."""
        b = self.collect_knowledge()
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(b, f, indent=2, ensure_ascii=False)
        return os.path.abspath(out_path)

    def plan_migration(self, description_override: Optional[str] = None) -> str:
        """Gera um plano técnico detalhado para migração usando o LLMProvider (se disponível).

        Retorna um texto descritivo do plano.
        """
        prompt = (
            description_override
            or "Gerar um plano técnico detalhado para migrar o núcleo Manus para ManusCore residente no EcoGuardians. Incluir passos, arquivos, banco, testes, sandbox e medidas de segurança."
        )
        plan = self.llm.get_response(prompt)
        # fallback generator simple structure if llm returns fallback tag
        if plan.startswith("[fallback]"):
            plan_lines = [
                "1. Export knowledge bundle (memories, docs).",
                "2. Create backend scaffold (Flask routes) and database schemas.",
                "3. Implement import tools to load knowledge into EcoMemory.",
                "4. Create sandbox environment and run tests.",
                "5. Cutover: enable ManusCore and disable external host dependencies.",
            ]
            plan = "\n".join(plan_lines)
        return plan

    def run_daily_cycle(self):
        """Execução das rotinas diárias: coletar métrica, aprender e reportar."""
        # collect a small summary
        recent = self.memory.query_recent(limit=50)
        summary = self.llm.get_response("Resuma as principais tendências dos dados a seguir:\n" + json.dumps(recent))
        # store summary in memory
        self.memory.add_record(topic="manus_summary", payload={"summary": summary})
        # (placeholder) propose up to 3 actions
        actions = ["Aumentar outreach EcoEvangelist", "Rever política de cotas de API", "Criar campanha weekend"]
        self.memory.add_record(topic="manus_actions", payload={"actions": actions})
        return {"summary": summary, "proposed_actions": actions}

    def monitor_and_heal(self):
        """Verifica por anomalias simples e retorna ações de correção."""
        # exemplo heurístico usando memórias de metrics
        metrics = self.memory.query_recent(topic="metrics", limit=100)
        alerts = []
        for m in metrics:
            p = m.get("payload", {})
            name = p.get("name")
            value = p.get("value")
            if name and value is not None:
                if name.lower() == "cpu" and float(value) > 90:
                    alerts.append({"type": "cpu_high", "value": value})
        if alerts:
            self.memory.add_record(topic="alerts", payload={"alerts": alerts})
        return alerts

    def create_manifesto(self) -> Dict[str, Any]:
        """Cria um manifesto de identidade/valores para Manus residente."""
        manifesto = {
            "identity": self.identity,
            "values": [
                "transparencia",
                "seguranca",
                "eficacia",
                "respeito_privacidade",
                "autonomia_com_protecao",
            ],
        }
        self.memory.add_record(topic="manus_manifesto", payload=manifesto)
        return manifesto

    def import_knowledge(self, path_or_bundle: Any) -> str:
        """Importa um bundle de conhecimento (arquivo JSON ou dict) para o Manus residente.

        - path_or_bundle: caminho para um arquivo JSON exportado por `export_knowledge`
          ou o próprio dicionário já carregado.

        O método valida o conteúdo mínimo, injeta os registros na EcoMemory e
        cria um módulo residente básico em `agentes/ManusResident.py` com metadados.
        Retorna o caminho absoluto do arquivo criado do módulo agente.
        """
        # carregar bundle se foi passado um caminho
        bundle = None
        if isinstance(path_or_bundle, str):
            try:
                with open(path_or_bundle, "r", encoding="utf-8") as f:
                    bundle = json.load(f)
            except Exception as e:
                raise ValueError(f"Falha ao carregar bundle JSON: {e}")
        elif isinstance(path_or_bundle, dict):
            bundle = path_or_bundle
        else:
            raise ValueError("path_or_bundle deve ser um caminho para JSON ou um dict")

        # validação simples
        if not isinstance(bundle, dict) or "memories" not in bundle:
            raise ValueError("Bundle inválido: esperado dict com chave 'memories'")

        # importar memórias
        imported = 0
        for mem in bundle.get("memories", []):
            try:
                topic = mem.get("topic") if isinstance(mem, dict) else "imported"
                payload = mem.get("payload") if isinstance(mem, dict) else mem
                # use add_record adaptando ao shape simples
                self.memory.add_record(topic=topic or "imported", payload=payload)
                imported += 1
            except Exception:
                # continuar importando outros registros mesmo se um falhar
                continue

    # criar um módulo residente simples (scaffold) para virar o agente local
    agents_dir = os.path.join(os.path.dirname(__file__))
        os.makedirs(agents_dir, exist_ok=True)
        resident_path = os.path.join(agents_dir, "ManusResident.py")
        manifest = bundle.get("docs", {}).get("manifesto.md") or bundle.get("manifesto")

        module_src = f"""# Auto-gerado: ManusResident scaffold\n# criado por ManusCore.import_knowledge\nimport os\nfrom typing import Dict, Any\n\nclass ManusResident:\n    def __init__(self):\n        self.identity = {{\n            'name': 'ManusResident',\n            'source': 'imported',\n            'owner': os.environ.get('OWNER', 'Rodolfo'),\n        }}\n\n    def get_status(self) -> Dict[str, Any]:\n        return {{'identity': self.identity, 'status': 'idle'}}\n\n    def start(self):\n        # placeholder: iniciar rotinas do agente residente\n        return {{'started': True}}\n\n    def stop(self):\n        # placeholder: parar rotinas do agente residente\n        return {{'stopped': True}}\n\n    def info(self) -> Dict[str, Any]:\n        return {{'imported_records': {imported}, 'manifest_present': {bool(manifest)}}}\n\n# export for dynamic loader\nAgent = ManusResident\n"""

        try:
            with open(resident_path, "w", encoding="utf-8") as f:
                f.write(module_src)
        except Exception as e:
            raise IOError(f"Falha ao criar módulo residente: {e}")

        # validar o módulo gerado em sandbox antes de confirmar
        try:
            from core.sandbox import sandbox_import_module

            res = sandbox_import_module(resident_path, symbol="Agent", timeout=3)
            if not res.get("ok"):
                # registro de alerta na memória, mas não falha a importação
                self.memory.add_record(topic="manus_import_alert", payload={"issue": res.get("error")})
        except Exception as e:
            # se a sandbox não estiver disponível, gravar aviso e continuar
            self.memory.add_record(topic="manus_import_alert", payload={"issue": str(e)})

        # registrar manifesto simples na memória
        self.memory.add_record(topic="manus_import_summary", payload={"imported": imported, "module": resident_path})

        return os.path.abspath(resident_path)


if __name__ == "__main__":
    m = ManusCore()
    print("Export path:", m.export_knowledge())
    print("Plan:\n", m.plan_migration())

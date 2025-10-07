# Agente mínimo de autoconstrucao (modo seguro por default)
import os
import subprocess
import tempfile
from git import Repo
from dotenv import load_dotenv
import openai
import textwrap
import pathlib
import sys

load_dotenv(dotenv_path=pathlib.Path(__file__).parents[1] / ".env")

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
MAX_ITERS = int(os.getenv("AGENT_MAX_ITERS", "3"))

if not OPENAI_KEY:
    print("OPENAI_API_KEY não configurada. Saindo.")
    sys.exit(1)

openai.api_key = OPENAI_KEY

REPO_PATH = pathlib.Path(__file__).parents[1].resolve()
repo = Repo(str(REPO_PATH))

def run_cmd(cmd, cwd=REPO_PATH):
    p = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

def check_linters_and_tests():
    out = {}
    rc, out["black"] = run_cmd("black --check . || true")
    rc, out["isort"] = run_cmd("isort --check-only . || true")
    rc, out["flake8"] = run_cmd("flake8 . || true")
    rc, out["pytest"] = run_cmd("pytest -q --maxfail=1 || true")
    return out

def prepare_prompt(failures):
    prompt = f"""
Você é um assistente dev prático. Repare nos outputs de lint/test abaixo (delimitados). Gere apenas um patch unificado (diff) que corrija os problemas.
Regras:
- Forneça somente o diff unificado (formato `git apply`).
- Mantenha mudanças pequenas e seguras.
- Explique no final em poucas linhas o que mudou (separado do diff por uma linha contendo somente '---').
Outputs:
{failures}
"""
    return prompt

def request_patch_from_llm(failures):
    prompt = prepare_prompt(failures)
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # use modelo disponível; ajuste conforme conta
        messages=[{"role":"system","content":"Você é um engenheiro de software que gera patches git."},
                  {"role":"user","content":prompt}],
        max_tokens=1500,
        temperature=0.0,
    )
    text = resp.choices[0].message.content
    return text

def apply_patch(patch_text):
    # salva patch temporário e aplica (ou só salva se DRY_RUN)
    with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
        tf.write(patch_text)
        tf.flush()
        if DRY_RUN:
            print("DRY_RUN ativo: patch salvo em", tf.name)
            print(patch_text[:2000])
            return False
        rc, out = run_cmd(f"git apply {tf.name}", cwd=REPO_PATH)
        if rc != 0:
            print("Falha ao aplicar patch:", out)
            return False
        run_cmd("git add -A", cwd=REPO_PATH)
        run_cmd('git commit -m "Autoconstructor: aplicar patch sugerido pelo LLM" || true', cwd=REPO_PATH)
        print("Patch aplicado e commit criado.")
        return True

def main_loop():
    for i in range(MAX_ITERS):
        print(f"[iter {i+1}/{MAX_ITERS}] rodando linters/testes...")
        results = check_linters_and_tests()
        combined = "\n\n".join(f"=== {k} ===\n{v}" for k,v in results.items())
        if all("FAILED" not in v and v.strip()=="" for v in results.values()):
            print("Tudo OK — nada a corrigir.")
            return
        print("Erros detectados — solicitando patch ao LLM...")
        patch = request_patch_from_llm(combined)
        # extrai diff (simples); assume LLM deu diff puro
        applied = apply_patch(patch)
        if applied and not DRY_RUN:
            # opcional: abrir PR se GITHUB_TOKEN disponível
            if GITHUB_TOKEN:
                print("Criar PR automático (não implementado por segurança).")
            print("Re-executando testes após patch...")
        else:
            print("Modo dry-run ou patch não aplicado; pare para revisão.")
            return

if __name__ == "__main__":
    main_loop()
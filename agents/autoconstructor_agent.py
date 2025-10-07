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
    main_loop()o    *** Begin Patch
    *** Add File: agents/autoconstructor_agent.py
    +#!/usr/bin/env python3
    +"""
    +Autoconstructor agent (modo seguro: DRY_RUN=true por padrão).
    +Analisa linters/tests e solicita patch ao LLM. Não aplica mudanças quando
    +DRY_RUN está true.
    +"""
    +import os
    +import subprocess
    +import tempfile
    +import pathlib
    +import sys
    +from dotenv import load_dotenv
    +
    +ROOT = pathlib.Path(__file__).parents[1].resolve()
    +load_dotenv(dotenv_path=ROOT / ".env")
    +
    +OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    +OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    +GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    +DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    +MAX_ITERS = int(os.getenv("AGENT_MAX_ITERS", "2"))
    +
    +try:
    +    import openai
    +    openai.api_key = OPENAI_API_KEY
    +except Exception:
    +    openai = None
    +
    +def run_cmd(cmd, cwd=ROOT, check=False):
    +    p = subprocess.run(cmd, shell=True, cwd=str(cwd), capture_output=True, text=True)
    +    out = (p.stdout or "") + (p.stderr or "")
    +    if check and p.returncode != 0:
    +        raise RuntimeError(f"Command failed: {cmd}\n{out}")
    +    return p.returncode, out
    +
    +def check_linters_and_tests():
    +    results = {}
    +    rc, out = run_cmd("black --check . || true")
    +    results["black"] = out
    +    rc2, out2 = run_cmd("isort --check-only . || true")
    +    results["isort"] = out2
    +    rc3, out3 = run_cmd("flake8 . || true")
    +    results["flake8"] = out3
    +    rc4, out4 = run_cmd("pytest -q --maxfail=1 || true")
    +    results["pytest"] = out4
    +    results["_codes"] = {"black": rc, "isort": rc2, "flake8": rc3, "pytest": rc4}
    +    return results
    +
    +def all_clean(results):
    +    codes = results.get("_codes", {})
    +    return all(v == 0 for v in codes.values())
    +
    +def prepare_prompt(failures_text):
    +    prompt = f"""
    +Você é um engenheiro de software que gera patches git (diff) para corrigir problemas de lint/test.
    +Regras:
    +- Retorne apenas o diff unificado aplicável por `git apply`.
    +- Após o diff, adicione uma linha com '---' e um resumo curto das mudanças.
    +Entrada (saídas dos comandos):
    +{failures_text}
    +"""
    +    return prompt.strip()
    +
    +def request_patch_from_llm(failures_text):
    +    if openai is None or not OPENAI_API_KEY:
    +        return None
    +    prompt = prepare_prompt(failures_text)
    +    try:
    +        resp = openai.ChatCompletion.create(
    +            model=OPENAI_MODEL,
    +            messages=[
    +                {"role": "system", "content": "Você gera patches git (diff) que corrigem erros de lint/test."},
    +                {"role": "user", "content": prompt},
    +            ],
    +            max_tokens=2000,
    +            temperature=0.0,
    +        )
    +        text = resp.choices[0].message.content
    +        return text
    +    except Exception as e:
    +        print("Erro ao chamar LLM:", e)
    +        return None
    +
    +def extract_diff(text):
    +    if not text:
    +        return None
    +    markers = ["diff --git", "+++ b/", "--- a/", "@@ "]
    +    if any(m in text for m in markers):
    +        start = text.find("diff --git")
    +        if start == -1:
    +            return text
    +        return text[start:]
    +    return None
    +
    +def apply_patch(patch_text):
    +    if not patch_text:
    +        print("Nenhum patch para aplicar.")
    +        return False
    +    diff = extract_diff(patch_text)
    +    if not diff:
    +        print("Não foi possível extrair diff do LLM. Salvando output para revisão.")
    +        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as tf:
    +            tf.write(patch_text)
    +            print("Output salvo em", tf.name)
    +        return False
    +    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".patch") as tf:
    +        tf.write(diff)
    +        tf.flush()
    +        print("Patch salvo em", tf.name)
    +        if DRY_RUN:
    +            print("DRY_RUN=true -> não aplicando patch automaticamente.")
    +            return False
    +        rc, out = run_cmd(f"git apply {tf.name}")
    +        if rc != 0:
    +            print("Falha ao aplicar patch:", out)
    +            return False
    +        run_cmd("git add -A")
    +        run_cmd('git commit -m "autoconstructor: aplicar patch sugerido pelo LLM" || true')
    +        print("Patch aplicado e commit criado.")
    +        return True
    +
    +def main():
    +    print("Autoconstructor agent — início (DRY_RUN={})".format(DRY_RUN))
    +    for i in range(MAX_ITERS):
    +        print(f"[iter {i+1}/{MAX_ITERS}] executando linters e testes...")
    +        results = check_linters_and_tests()
    +        if all_clean(results):
    +            print("Linters/tests limpos. Nada a fazer.")
    +            return
    +        combined = "\n\n".join(f"=== {k} ===\n{v}" for k, v in results.items() if k != "_codes")
    +        print("Problemas detectados. Solicitando patch ao LLM...")
    +        patch = request_patch_from_llm(combined)
    +        if not patch:
    +            print("Nenhum patch gerado (LLM indisponível ou erro). Saída para revisão.")
    +            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as tf:
    +                tf.write(combined)
    +                print("Saída dos erros salva em", tf.name)
    +            return
    +        applied = apply_patch(patch)
    +        if not applied:
    +            print("Patch não aplicado (modo dry-run ou falha). Parando para revisão humana.")
    +            return
    +        else:
    +            print("Patch aplicado. Re-executando validações...")
    +    print("Limite de iterações atingido. Finalizando.")
    +
    +if __name__ == "__main__":
    +    main()
    +
    *** End Patch
    *** Begin Patch
    *** Add File: .env.example
    +# Exemplo de .env — NUNCA comite chaves reais.
    +# Copie -> .env e preencha com suas credenciais.
    +OPENAI_API_KEY=
    +OPENAI_MODEL=gpt-4o-mini
    +GITHUB_TOKEN=
    +DRY_RUN=true
    +AGENT_MAX_ITERS=2
    +
    *** End Patch
    *** Begin Patch
    *** Add File: .github/workflows/autoconstructor.yml
    +name: Autoconstructor Agent (dry-run)
    +
    +on:
    +  workflow_dispatch:
    +  schedule:
    +    - cron: '0 3 * * *' # diário às 03:00 UTC
    +
    +jobs:
    +  run-agent:
    +    runs-on: ubuntu-latest
    +    steps:
    +      - uses: actions/checkout@v4
    +      - name: Setup Python
    +        uses: actions/setup-python@v4
    +        with:
    +          python-version: '3.11'
    +      - name: Install deps
    +        run: |
    +          python -m pip install --upgrade pip
    +          pip install -r requirements.txt
    +          pip install gitpython python-dotenv openai
    +      - name: Run agent (DRY_RUN)
    +        env:
    +          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    +          DRY_RUN: "true"
    +        run: |
    +          python agents/autoconstructor_agent.py
    +
    *** End Patch
    *** End Patch
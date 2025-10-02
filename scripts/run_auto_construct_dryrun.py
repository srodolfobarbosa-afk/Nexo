#!/usr/bin/env python3
"""Script de dry-run para auto-construction.
Ele instancia o AutoConstructionModule com um LLM stub (por segurança) e pede
uma construção em modo staging. Resultados são salvos em autoconstruct_staging/."""
import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auto_construction import AutoConstructionModule


def llm_stub(prompt, context):
    # Resposta segura e simples para dry-run: sugere criação de um arquivo README
    return json.dumps({
        "files": {
            "autoconstruct_generated/README.md": "# Generated\n\nEste é um artefato gerado em modo dry-run."
        },
        "installation_commands": []
    })


def main():
    ac = AutoConstructionModule(llm_stub)
    feature = os.environ.get('AUTO_CONSTRUCT_FEATURE', 'Improve README and add diagnostics')
    print(f"[dry-run] Running auto_construct_feature for: {feature}")
    result = ac.auto_construct_feature(feature)
    out = {
        'timestamp': datetime.now().isoformat(),
        'feature': feature,
        'result': result
    }
    out_path = os.path.join(os.getcwd(), 'autoconstruct_staging', f"dryrun_{int(datetime.now().timestamp())}")
    os.makedirs(out_path, exist_ok=True)
    with open(os.path.join(out_path, 'meta.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"[dry-run] Meta saved to {out_path}/meta.json")


if __name__ == '__main__':
    main()

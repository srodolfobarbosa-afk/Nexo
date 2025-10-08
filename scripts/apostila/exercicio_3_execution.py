#!/usr/bin/env python3
"""Gera checklist para criar um agente EcoEdu (exercício 3)"""
import json
import os

checklist = {
    "agent_name": "EcoEdu",
    "steps": [
        "1. Definir responsabilidades do agente",
        "2. Criar prompt base e ferramentas (LLM, DB access)",
        "3. Gerar scaffold de código (agentes/EcoEdu.py)",
        "4. Escrever testes unitários",
        "5. Rodar pipeline CI de validação",
        "6. Deploy e registrar no agent_registry",
    ],
}

out = os.path.abspath("apostila_ex3_checklist.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(checklist, f, ensure_ascii=False, indent=2)

print("Checklist salvo em:", out)

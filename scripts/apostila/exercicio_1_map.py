#!/usr/bin/env python3
"""Gera um JSON simples com o fluxo do exercício 1"""
import json
import os

flow = {
    "user_command": "Crie relatório semanal de vendas",
    "orchestrator": "NexoGenesis",
    "agent": "EcoFinance",
    "memory_write": {"table": "reports", "id": 1},
    "report": "report_2025-10-08.pdf",
}

out = os.path.abspath("apostila_ex1_flow.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(flow, f, ensure_ascii=False, indent=2)

print("Flow saved to:", out)

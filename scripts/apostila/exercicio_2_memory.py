#!/usr/bin/env python3
"""Simula consulta de memória para o exercício 2"""
import json
import os

log = [
    {"id": 1, "user": "A", "action": "purchase", "amount": 100, "result": "success"},
    {"id": 2, "user": "A", "action": "refund", "amount": 50, "result": "success"},
    {"id": 3, "user": "B", "action": "purchase", "amount": 200, "result": "failed"},
    {"id": 4, "user": "A", "action": "purchase", "amount": 300, "result": "success"},
    {"id": 5, "user": "C", "action": "inquiry", "amount": 0, "result": "info"},
]

out = os.path.abspath("apostila_ex2_log.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)

print("Log salvo em:", out)

# Consulta exemplo
recent_a = [r for r in log if r["user"] == "A"]
print("Historico do usuário A:")
print(json.dumps(recent_a, indent=2, ensure_ascii=False))

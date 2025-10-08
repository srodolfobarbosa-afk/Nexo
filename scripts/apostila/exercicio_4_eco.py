#!/usr/bin/env python3
"""Simula entrada de receita e distribuição (exercício 4)"""
import csv
import os

amount = 1000.0
rodolfo = round(amount * 0.30, 2)
reinvest = round(amount * 0.70, 2)

out_csv = os.path.abspath("apostila_ex4_eco.csv")
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["descricao", "valor", "destino"])
    writer.writerow(["receita_simulada", amount, "entrada"])
    writer.writerow(["rodolfo", rodolfo, "distribuicao"])
    writer.writerow(["reinvestimento", reinvest, "distribuicao"])

print("CSV gerado em:", out_csv)
print(f"Saldo: R${amount} | Rodolfo: R${rodolfo} | Reinvestimento: R${reinvest}")

#!/usr/bin/env python3
"""Backup simples do SQLite local usado pela EcoMemory.

Localiza `data/eco_memory.db` e gera um arquivo com timestamp em `data/backups/`.
"""
import os
import shutil
import datetime


def main():
    src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "eco_memory.db"))
    if not os.path.exists(src):
        print("No local DB found at", src)
        return
    dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "backups"))
    os.makedirs(dest_dir, exist_ok=True)
    now = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = os.path.join(dest_dir, f"eco_memory_backup_{now}.db")
    shutil.copy2(src, dest)
    print("Backup created at", dest)


if __name__ == "__main__":
    main()

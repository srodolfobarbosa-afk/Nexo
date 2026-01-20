#!/usr/bin/env python3
"""
🔧 NEXO AUTO-FIX: Corretor automático de Python
Remove erros de indentação e sintaxe complexos
"""

import sys
from pathlib import Path
from io import StringIO
import re

def autopep8_fix(content):
    """Aplica fixes automáticos ao código"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Remover indentação excessiva após comentários
        if line and not line[0].isspace() and i > 0:
            prev = fixed_lines[-1] if fixed_lines else ""
            if prev.strip().startswith('#'):
                # Linha que segue comentário não deve ter indent extra
                fixed_lines.append(line.lstrip())
                continue
        
        # Normalizar indentação: converter tabs em 4 espaços
        if '\t' in line:
            line = line.replace('\t', '    ')
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def validate_and_fix(filepath):
    """Valida e tenta corrigir arquivo"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tentar compilar original
        try:
            compile(content, str(filepath), 'exec')
            print(f"✅ {filepath.name} - OK")
            return True
        except SyntaxError as e:
            print(f"⚠️ {filepath.name} - Erro na linha {e.lineno}: {e.msg}")
            
            # Tentar fix automático
            fixed = autopep8_fix(content)
            
            try:
                compile(fixed, str(filepath), 'exec')
                # Se conseguiu compilar, salvar
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                print(f"✅ {filepath.name} - CORRIGIDO!")
                return True
            except:
                # Se ainda falhar, tentar remover linhas problemáticas
                try:
                    lines = content.split('\n')
                    filtered = []
                    for i, line in enumerate(lines):
                        # Pular linhas que começam com espaços depois de comentário
                        if i > 0 and line.strip().startswith('try:') and lines[i-1].strip().startswith('#'):
                            filtered.append(line.lstrip())
                        elif i > 0 and line and line[0].isspace() and (i == 0 or not lines[i-1].strip() or lines[i-1].strip().startswith('#')):
                            filtered.append(line.lstrip())
                        else:
                            filtered.append(line)
                    
                    final = '\n'.join(filtered)
                    compile(final, str(filepath), 'exec')
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(final)
                    print(f"✅ {filepath.name} - REPARADO (modo agressivo)!")
                    return True
                except Exception as ex:
                    print(f"❌ {filepath.name} - Não foi possível reparar: {ex}")
                    return False
    except Exception as e:
        print(f"❌ {filepath.name} - Erro ao processar: {e}")
        return False

if __name__ == "__main__":
    root = Path("/workspaces/rodolfo")
    
    print("=" * 60)
    print("🔧 NEXO AUTO-FIX: Limpando erros de Python...")
    print("=" * 60)
    
    py_files = [
        root / "app.py",
        root / "bot_engenheiro_v2.py",
        root / "deus.py",
        root / "bot_engenheiro.py",
        root / "nexo_guardiao.py",
    ]
    
    results = {}
    for f in py_files:
        if f.exists():
            results[f.name] = validate_and_fix(f)
    
    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    fixed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"✅ Corrigidos: {fixed}/{total}")
    print("=" * 60)
    
    sys.exit(0 if fixed == total else 1)

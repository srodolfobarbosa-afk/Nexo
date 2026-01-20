#!/usr/bin/env python3
"""
🤖 AUTO-VALIDATOR NEXO v2026
Sistema automático de validação, reparação e monitoramento
"""

import ast
import os
import sys
import re
from pathlib import Path
from loguru import logger
import subprocess
from datetime import datetime

# Configurar logger
logger.remove()
logger.add(sys.stderr, format="<level>{level: <8}</level> | {message}")
try:
    logger.add("/workspaces/rodolfo/logs/auto_validator.log", rotation="500 MB")
except:
    pass  # Se /app/logs não existir, apenas usa stderr

class AutoValidator:
    """Sistema inteligente de validação e auto-reparação"""
    
    def __init__(self, root_path=None):
        if root_path is None:
            root_path = os.path.dirname(os.path.abspath(__file__))
        self.root_path = Path(root_path)
        self.py_files = []
        self.errors = []
        self.fixed = []
        
    def scan_python_files(self):
        """Escaneia todos os arquivos Python"""
        logger.info("🔍 Escaneando arquivos Python...")
        self.py_files = list(self.root_path.rglob("*.py"))
        logger.success(f"✅ {len(self.py_files)} arquivos encontrados")
        return self.py_files
    
    def validate_syntax(self, filepath):
        """Valida sintaxe Python"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, e
    
    def fix_indentation(self, filepath):
        """Corrige erros de indentação comuns"""
        logger.info(f"🔧 Corrigindo indentação em {filepath.name}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            fixed_lines = []
            for i, line in enumerate(lines):
                # Remover indentação excessiva em linhas após comentários
                if line.strip().startswith('try:') and i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line.startswith('#'):
                        # Encontrar indentação apropriada
                        proper_indent = 0
                        fixed_lines.append(' ' * proper_indent + line.lstrip())
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            logger.success(f"✅ Indentação corrigida em {filepath.name}")
            self.fixed.append(str(filepath))
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir {filepath.name}: {e}")
            return False
    
    def fix_imports(self, filepath):
        """Corrige imports inválidos"""
        logger.info(f"📦 Corrigindo imports em {filepath.name}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix: "from langchain.agents import AgentExecutor, create_react_agent" → "from langchain.agents from langchain.agents import AgentExecutor, create_react_agent"
            fixes = [
                (r'from langchain.agents import AgentExecutor, create_react_agent',
                 'from langchain.agents from langchain.agents import AgentExecutor, create_react_agent'),
            ]
            
            original = content
            for old, new in fixes:
                content = re.sub(old, new, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.success(f"✅ Imports corrigidos em {filepath.name}")
                self.fixed.append(str(filepath))
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir imports: {e}")
            return False
    
    def run_all_checks(self):
        """Executa validação completa"""
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO AUTO-VALIDAÇÃO DO SISTEMA")
        logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        self.scan_python_files()
        
        for filepath in self.py_files:
            logger.info(f"\n📄 Validando {filepath.name}...")
            
            # Validar sintaxe
            is_valid, error = self.validate_syntax(filepath)
            if not is_valid:
                logger.error(f"❌ Erro de sintaxe: {error}")
                self.errors.append({
                    'file': str(filepath),
                    'error': str(error),
                    'type': 'syntax'
                })
                
                # Tentar reparar
                if isinstance(error, SyntaxError):
                    if 'indent' in str(error).lower():
                        self.fix_indentation(filepath)
                    
                    # Revalidar após reparos
                    is_valid, error = self.validate_syntax(filepath)
                    if is_valid:
                        logger.success(f"✅ {filepath.name} reparado!")
                    else:
                        logger.error(f"❌ Falha ao reparar {filepath.name}")
            else:
                logger.success(f"✅ {filepath.name} válido")
            
            # Corrigir imports
            self.fix_imports(filepath)
        
        self.report()
    
    def report(self):
        """Gera relatório final"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO FINAL")
        logger.info("=" * 60)
        logger.info(f"✅ Arquivos corrigidos: {len(self.fixed)}")
        logger.info(f"❌ Erros encontrados: {len(self.errors)}")
        
        if self.fixed:
            logger.info("\n📝 Arquivos reparados:")
            for f in self.fixed:
                logger.info(f"   ✅ {f}")
        
        if self.errors:
            logger.info("\n⚠️ Erros não resolvidos:")
            for err in self.errors:
                logger.error(f"   ❌ {err['file']}: {err['error']}")
        
        if not self.errors:
            logger.success("\n🎉 SISTEMA 100% VALIDADO E OPERACIONAL!")
        
        logger.info("=" * 60)

def auto_build_and_monitor():
    """Auto-constrói e monitora o sistema"""
    validator = AutoValidator()
    validator.run_all_checks()
    return len(validator.errors) == 0

if __name__ == "__main__":
    success = auto_build_and_monitor()
    sys.exit(0 if success else 1)

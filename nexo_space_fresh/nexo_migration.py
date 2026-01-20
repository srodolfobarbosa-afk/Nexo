#!/usr/bin/env python3
"""
🚀 NEXO AUTO-MIGRATION SYSTEM v2026
Auto-detecta incompatibilidades e migra para ambientes compatíveis
Sistema autônomo de evolução e auto-reparação
"""

import subprocess
import sys
import os
from pathlib import Path
import re
import json
from datetime import datetime

class EnvironmentMigrator:
    """Gerencia migração automática entre ambientes"""
    
    def __init__(self):
        self.root = Path("/workspaces/rodolfo")
        self.backup_dir = self.root / "migrations"
        self.backup_dir.mkdir(exist_ok=True)
        self.log_file = self.backup_dir / "migration.log"
    
    def log(self, msg):
        """Registra eventos de migração"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def detect_environment(self):
        """Detecta ambiente de execução"""
        if os.path.exists("/.dockerenv"):
            return "docker"
        elif os.path.exists("/app"):
            return "hf_spaces"
        else:
            return "local"
    
    def detect_incompatibilities(self):
        """Detecta problemas de compatibilidade"""
        issues = []
        
        # Check Python version
        py_version = sys.version_info
        if py_version.major == 3 and py_version.minor == 12:
            self.log("ℹ️ Python 3.12 detectado - pode ter issues com pydantic/langsmith")
            issues.append("python_3_12_pydantic_issue")
        
        # Check pydantic version
        try:
            import pydantic
            pydantic_version = pydantic.__version__
            if pydantic_version.startswith("2"):
                self.log(f"⚠️ Pydantic {pydantic_version} detectado (v2)")
                issues.append("pydantic_v2_compatibility")
        except:
            pass
        
        return issues
    
    def fix_pydantic_langsmith(self):
        """Corrige incompatibilidade pydantic/langsmith"""
        self.log("🔧 Corrigindo pydantic/langsmith...")
        
        req_file = self.root / "requirements.txt"
        with open(req_file, 'r') as f:
            content = f.read()
        
        # Backup
        backup_file = self.backup_dir / f"requirements.bak.{datetime.now().strftime('%s')}"
        with open(backup_file, 'w') as f:
            f.write(content)
        self.log(f"💾 Backup salvo: {backup_file}")
        
        # Fix 1: Downgrade pydantic para versão compatível
        content = re.sub(r'pydantic==.*', 'pydantic==2.0.3', content)
        
        # Fix 2: Adicionar langchain-core (mais leve)
        if 'langchain-core' not in content:
            content += '\nlangchain-core==0.1.8\n'
        
        # Fix 3: Remove langsmith (causa conflito)
        content = re.sub(r'langsmith==.*\n', '', content)
        
        # Fix 4: Simplificar langchain deps
        content = re.sub(r'langchain==.*', 'langchain==0.0.352', content)
        
        with open(req_file, 'w') as f:
            f.write(content)
        
        self.log("✅ requirements.txt atualizado")
        return True
    
    def fix_app_imports(self):
        """Remove imports problemáticos de app.py"""
        self.log("🔧 Corrigindo imports de app.py...")
        
        app_file = self.root / "app.py"
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Backup
        backup_file = self.backup_dir / f"app.py.bak.{datetime.now().strftime('%s')}"
        with open(backup_file, 'w') as f:
            f.write(content)
        self.log(f"💾 Backup app.py: {backup_file}")
        
        # Remove imports problemáticos
        problematic = [
            r'from langchain\.agents import load_tools.*\n',
            r'import AgentExecutor.*\n',
        ]
        
        for pattern in problematic:
            if re.search(pattern, content):
                content = re.sub(pattern, '', content)
                self.log(f"✂️ Removido import problemático: {pattern}")
        
        # Adicionar imports seguros
        if 'from langchain_groq' in content and 'from langchain.chat_models import ChatGroq' not in content:
            # Já usa langchain_groq, não precisa de mais nada
            pass
        
        with open(app_file, 'w') as f:
            f.write(content)
        
        self.log("✅ app.py atualizado")
        return True
    
    def reinstall_dependencies(self):
        """Reinstala dependências no container"""
        self.log("📦 Reinstalando dependências...")
        
        try:
            result = subprocess.run(
                ["pip", "install", "--upgrade", "--force-reinstall", "-r", str(self.root / "requirements.txt")],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log("✅ Dependências instaladas com sucesso")
                return True
            else:
                self.log(f"❌ Erro ao instalar: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"❌ Exceção: {e}")
            return False
    
    def migrate(self):
        """Executa migração completa"""
        self.log("\n" + "="*60)
        self.log("🚀 INICIANDO AUTO-MIGRATION NEXO v2026")
        self.log("="*60)
        
        env = self.detect_environment()
        self.log(f"📍 Ambiente detectado: {env}")
        
        issues = self.detect_incompatibilities()
        self.log(f"🔍 Problemas encontrados: {len(issues)}")
        for issue in issues:
            self.log(f"   - {issue}")
        
        if "pydantic_v2_compatibility" in issues or "python_3_12_pydantic_issue" in issues:
            self.fix_pydantic_langsmith()
            self.fix_app_imports()
            
            if env in ["docker", "hf_spaces"]:
                self.reinstall_dependencies()
        
        self.log("🎉 Migração concluída!")
        self.log("="*60 + "\n")

if __name__ == "__main__":
    migrator = EnvironmentMigrator()
    migrator.migrate()

"""Inicializador simples de banco (SQLite por padrão).
Cria tabelas minimais usadas nos testes e no runtime (memories, agent logs).
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class Memory(Base):
    __tablename__ = 'memory'
    id = Column(Integer, primary_key=True)
    key = Column(String(255), index=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentLog(Base):
    __tablename__ = 'agent_error_log'
    id = Column(Integer, primary_key=True)
    agent = Column(String(255))
    level = Column(String(50))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def main():
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///nexo_local.db'
    engine = create_engine(DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    print(f"DB initialized at {DATABASE_URL}")

if __name__ == '__main__':
    main()

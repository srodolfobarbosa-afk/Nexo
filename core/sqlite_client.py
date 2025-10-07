"""SQLite fallback client usando SQLAlchemy para persistência local.

Fornece tabelas simples: memories, tasks, agent_logs, revenue
"""

import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("NEXO_SQLITE_URL", "sqlite:///./nexo_data.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), index=True)
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    status = Column(String(32), default="pending")
    result = Column(Text, nullable=True)
    reward = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)


class AgentLog(Base):
    __tablename__ = "agent_logs"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(32))
    message = Column(Text)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Revenue(Base):
    __tablename__ = "revenue"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()


def save_memory_local(key: str, data: str):
    s = get_session()
    try:
        m = Memory(key=key, data=data)
        s.add(m)
        s.commit()
    finally:
        s.close()


def save_task_local(
    name: str, status: str = "pending", result: str = None, reward: float = 0.0
):
    s = get_session()
    try:
        t = Task(name=name, status=status, result=result, reward=reward)
        s.add(t)
        s.commit()
        return t.id
    finally:
        s.close()


def save_log_local(level: str, message: str, details: str = None):
    s = get_session()
    try:
        l = AgentLog(level=level, message=message, details=details)
        s.add(l)
        s.commit()
    finally:
        s.close()


def add_revenue(amount: float):
    s = get_session()
    try:
        r = Revenue(amount=amount)
        s.add(r)
        s.commit()
    finally:
        s.close()


def get_total_revenue() -> float:
    s = get_session()
    try:
        total = s.query(Revenue).with_entities(func_sum(Revenue.amount)).scalar() or 0.0
        return float(total)
    finally:
        s.close()


def list_tasks(limit: int = 50):
    s = get_session()
    try:
        return s.query(Task).order_by(Task.created_at.desc()).limit(limit).all()
    finally:
        s.close()


# local import to avoid circular reference
from sqlalchemy import func as _func

func_sum = _func.sum

init_db()

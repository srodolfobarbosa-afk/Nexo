"""SQLite client with a lightweight fallback when SQLAlchemy is not installed.

If SQLAlchemy is available, we use it for a richer ORM. Otherwise we provide a
minimal sqlite3-based implementation that supports the operations used by the
rest of the code (init_db, save_log_local, save_task_local, etc.). This
avoids forcing SQLAlchemy installation in lightweight test environments.
"""
import os
from datetime import datetime
import json

_USE_SQLALCHEMY = True
try:
    from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, Float, DateTime
    from sqlalchemy.orm import declarative_base, sessionmaker
except Exception:
    _USE_SQLALCHEMY = False

DATABASE_URL = os.environ.get('NEXO_SQLITE_URL', 'sqlite:///./nexo_data.db')

if _USE_SQLALCHEMY:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base = declarative_base()
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


    class Memory(Base):
        __tablename__ = 'memories'
        id = Column(Integer, primary_key=True, index=True)
        key = Column(String(128), index=True)
        data = Column(Text)
        created_at = Column(DateTime, default=datetime.utcnow)


    class Task(Base):
        __tablename__ = 'tasks'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(256))
        status = Column(String(32), default='pending')
        result = Column(Text, nullable=True)
        reward = Column(Float, default=0.0)
        created_at = Column(DateTime, default=datetime.utcnow)
        finished_at = Column(DateTime, nullable=True)


    class AgentLog(Base):
        __tablename__ = 'agent_logs'
        id = Column(Integer, primary_key=True, index=True)
        level = Column(String(32))
        message = Column(Text)
        details = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)


    class Revenue(Base):
        __tablename__ = 'revenue'
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


    def save_task_local(name: str, status: str = 'pending', result: str = None, reward: float = 0.0):
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
            from sqlalchemy import func as _func
            total = s.query(Revenue).with_entities(_func.sum(Revenue.amount)).scalar() or 0.0
            return float(total)
        finally:
            s.close()


    def list_tasks(limit: int = 50):
        s = get_session()
        try:
            return s.query(Task).order_by(Task.created_at.desc()).limit(limit).all()
        finally:
            s.close()


    init_db()
else:
    # Fallback mínimo usando sqlite3 embutido
    import sqlite3

    DB_PATH = os.environ.get('NEXO_SQLITE_PATH', './nexo_data.db')

    def _conn():
        return sqlite3.connect(DB_PATH)

    def init_db():
        c = _conn()
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, message TEXT, details TEXT, created_at TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status TEXT, result TEXT, reward REAL, created_at TEXT, finished_at TEXT)''')
            c.commit()
        finally:
            c.close()

    def save_memory_local(key: str, data: str):
        c = _conn()
        try:
            c.execute('INSERT INTO agent_logs (level, message, details, created_at) VALUES (?, ?, ?, ?)', ('info', f'memory:{key}', data, datetime.utcnow().isoformat()))
            c.commit()
        finally:
            c.close()

    def save_task_local(name: str, status: str = 'pending', result: str = None, reward: float = 0.0):
        c = _conn()
        try:
            c.execute('INSERT INTO tasks (name, status, result, reward, created_at) VALUES (?, ?, ?, ?, ?)', (name, status, result, reward, datetime.utcnow().isoformat()))
            c.commit()
            return c.lastrowid
        finally:
            c.close()

    def save_log_local(level: str, message: str, details: str = None):
        c = _conn()
        try:
            c.execute('INSERT INTO agent_logs (level, message, details, created_at) VALUES (?, ?, ?, ?)', (level, message, details, datetime.utcnow().isoformat()))
            c.commit()
        finally:
            c.close()

    def add_revenue(amount: float):
        # fallback: log revenue event
        save_log_local('info', f'revenue_added:{amount}', None)

    def get_total_revenue() -> float:
        # fallback: not implemented accurately
        return 0.0

    def list_tasks(limit: int = 50):
        c = _conn()
        try:
            cur = c.execute('SELECT id, name, status, result, reward, created_at FROM tasks ORDER BY created_at DESC LIMIT ?', (limit,))
            return cur.fetchall()
        finally:
            c.close()


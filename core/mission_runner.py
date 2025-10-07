"""Mission runner simples para simular execução de missões que geram receita.

Roda em background e processa uma fila de tarefas: cria tasks, marca como concluídas e adiciona receita.
"""

import logging
import threading
import time
from datetime import datetime
from random import choice, random

from . import sqlite_client
from .supabase_client import save_log, save_task

logger = logging.getLogger("mission_runner")

_stop = False


def run_once():
    """Cria uma tarefa, processa e registra receita."""
    task_name = f"mission-{int(datetime.utcnow().timestamp())}"
    reward = round(10 + random() * 90, 2)  # R$ 10-100
    logger.info(f"Criando tarefa {task_name} com recompensa R${reward}")
    # persistir task
    try:
        sqlite_client.save_task_local(task_name, status="running")
        save_task("tasks", {"name": task_name, "status": "running", "reward": reward})
    except Exception as e:
        logger.error(f"Erro ao salvar tarefa: {e}")

    # simula execução (random delay)
    time.sleep(1 + random() * 3)
    success = random() > 0.1
    status = "done" if success else "failed"
    result = "ok" if success else "error"
    try:
        sqlite_client.save_task_local(
            task_name, status=status, result=result, reward=reward
        )
        save_task(
            "tasks",
            {"name": task_name, "status": status, "result": result, "reward": reward},
        )
    except Exception as e:
        logger.error(f"Erro atualizando tarefa: {e}")

    if success:
        try:
            sqlite_client.add_revenue(reward)
            save_log("info", f"Task {task_name} completed, revenue {reward}")
        except Exception as e:
            logger.error(f"Erro ao registrar receita: {e}")
    else:
        save_log("warning", f"Task {task_name} failed")


def runner_loop(interval: int = 5):
    logger.info("Mission runner started")
    while not _stop:
        try:
            run_once()
        except Exception as e:
            logger.error(f"Exception in mission loop: {e}")
        time.sleep(interval)
    logger.info("Mission runner stopped")


def start_background(interval: int = 5):
    t = threading.Thread(target=runner_loop, args=(interval,), daemon=True)
    t.start()
    return t


def stop_runner():
    global _stop
    _stop = True

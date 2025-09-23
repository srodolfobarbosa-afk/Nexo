"""Mission runner simples para simular execução de missões que geram receita.

Roda em background e processa uma fila de tarefas: cria tasks, marca como concluídas e adiciona receita.
"""
import threading
import time
import logging
from random import random, choice
from datetime import datetime
from queue import Queue, Empty

_task_queue = Queue()

from . import sqlite_client
from .supabase_client import save_task, save_log
import os
from .database import get_supabase_client

logger = logging.getLogger('mission_runner')

_stop = False


def run_once():
    """Cria uma tarefa, processa e registra receita."""
    # Try to get a task from the queue; if none, create a new one
    try:
        task = _task_queue.get_nowait()
        task_name = task.get('name')
        reward = task.get('reward', 0.0)
        created_by_queue = True
    except Empty:
        created_by_queue = False
        task_name = f"mission-{int(datetime.utcnow().timestamp())}"
        reward = round(10 + random() * 90, 2)  # R$ 10-100

    logger.info(f"Processing task {task_name} (reward R${reward})")

    # idempotency: check if task already exists in sqlite (by name)
    try:
        sqlite_client.save_task_local(task_name, status='running')
        save_task('tasks', {'name': task_name, 'status': 'running', 'reward': reward})
    except Exception as e:
        logger.error(f"Erro ao salvar tarefa inicial: {e}")

    # execute with retry/backoff
    attempts = 0
    max_attempts = 3
    success = False
    while attempts < max_attempts and not success:
        attempts += 1
        delay = 1 + random() * 2 * attempts
        time.sleep(delay)
        success = random() > 0.1
        if not success:
            logger.warning(f'Task {task_name} attempt {attempts} failed; retrying...')

    status = 'done' if success else 'failed'
    result = 'ok' if success else 'error'
    try:
        sqlite_client.save_task_local(task_name, status=status, result=result, reward=reward)
        save_task('tasks', {'name': task_name, 'status': status, 'result': result, 'reward': reward})
    except Exception as e:
        logger.error(f"Erro atualizando tarefa: {e}")

    if success:
        try:
            sqlite_client.add_revenue(reward)
            save_log('info', f'Task {task_name} completed, revenue {reward}')
        except Exception as e:
            logger.error(f"Erro ao registrar receita: {e}")
    else:
        save_log('warning', f'Task {task_name} failed after {attempts} attempts')

    # mark queue task as done
    if created_by_queue:
        try:
            _task_queue.task_done()
        except Exception:
            pass


def runner_loop(interval: int = 5):
    logger.info('Mission runner started')
    while not _stop:
        try:
            start_flag = os.environ.get('START_MISSION_RUNNER', '1')
            if str(start_flag).lower() not in ('1', 'true'):
                logger.info('Mission runner desativado via START_MISSION_RUNNER env')
            else:
                supabase = get_supabase_client()
                if supabase:
                    run_once()
                else:
                    logger.warning('Supabase indisponível — mission runner aguardando configuração')
        except Exception as e:
            logger.error(f'Exception in mission loop: {e}')
        time.sleep(interval)
    logger.info('Mission runner stopped')


def start_background(interval: int = 5):
    t = threading.Thread(target=runner_loop, args=(interval,), daemon=True)
    t.start()
    return t


def stop_runner():
    global _stop
    _stop = True

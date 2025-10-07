"""Simple RQ worker example for scheduling agent.run_once jobs.

Requires Redis running (e.g., via docker-compose). This file provides a
job function and a minimal scheduler example.
"""

import time

from redis import Redis
from rq import Queue

redis_conn = Redis(host="redis", port=6379, db=0)
q = Queue("default", connection=redis_conn)


def run_agent_once(agent_class_path: str, config: dict):
    """Dynamically import an agent and run it once.

    agent_class_path = 'module.sub:ClassName'
    """
    module_path, class_name = agent_class_path.split(":")
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    agent = cls(config, storage=None)
    return agent.run_once({})


def schedule_example():
    # Schedule a job every 60 seconds (demo; replace with real scheduler)
    while True:
        job = q.enqueue(run_agent_once, "agents.NexoGenesis:NexoGenesisAgent", {})
        print("Enqueued job:", job.id)
        time.sleep(60)


if __name__ == "__main__":
    schedule_example()

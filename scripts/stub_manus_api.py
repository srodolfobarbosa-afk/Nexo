#!/usr/bin/env python3
"""Stub HTTP server that simula parte da API do Manus para testes locais.

Endpoints:
- POST /tasks -> retorna tarefa criada com id
- GET /tasks/<id> -> retorna status
"""
from flask import Flask, request, jsonify
import uuid
import time

app = Flask(__name__)
_store = {}


@app.route("/tasks", methods=["POST"])
def create_task():
    payload = request.get_json(silent=True) or {}
    tid = str(uuid.uuid4())
    _store[tid] = {"id": tid, "status": "queued", "payload": payload, "created_at": time.time()}
    return jsonify({"id": tid, "status": "queued", "message": "task accepted in stub"}), 201


@app.route("/tasks/<tid>", methods=["GET"])
def get_task(tid):
    t = _store.get(tid)
    if not t:
        return jsonify({"error": "not_found"}), 404
    # simple progression
    age = time.time() - t["created_at"]
    if age > 2:
        t["status"] = "completed"
        t["result"] = {"insight": "stub-insight", "ok": True}
    return jsonify(t)


if __name__ == "__main__":
    app.run(port=5001)

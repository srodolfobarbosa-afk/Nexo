
#!/bin/bash
# start.sh corrigido para produção Nexo
set -e

# Ativa o ambiente virtual se existir
if [ -d ".venv" ]; then
	source .venv/bin/activate
elif [ -d "venv" ]; then
	source venv/bin/activate
fi

# Inicia o backend Flask principal (main.py) e o servidor WebSocket (ws_server.py) em paralelo
# Ambos servem a pasta app/static

# Inicia o backend Flask (porta 5000)
python3 src/main.py &
FLASK_PID=$!

# Inicia o servidor WebSocket (porta 8000)
python3 src/ws_server.py &
WS_PID=$!

# Espera ambos terminarem
wait $FLASK_PID $WS_PID

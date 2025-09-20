// script.js - Centro de Comando EcoGuardians

// WebSocket para receber dados dos agentes
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'monitor') {
        // Suporta até 3 partes visuais
        if (Array.isArray(data.content)) {
            for (let i = 0; i < 3; i++) {
                document.getElementById('monitor-content-' + (i+1)).innerHTML = data.content[i] || '';
            }
        } else {
            document.getElementById('monitor-content-1').innerHTML = data.content;
        }
    }
    if (data.type === 'agentes_status') {
        renderAgentesCards(data.agentes);
    }
    if (data.type === 'financeiro') {
        document.getElementById('financeiro-graficos').innerHTML = data.graficos;
    }
    if (data.type === 'historico') {
        window.allLogs = data.logs || [];
        renderHistoricoLogs(window.allLogs);
    }
    if (data.type === 'mapa_tarefas') {
        document.getElementById('mapa-content').innerHTML = data.mapa;
    }
    if (data.type === 'config') {
        document.getElementById('config-content').innerHTML = data.config;
    }
};
function renderHistoricoLogs(logs) {
    const nivel = document.getElementById('filtro-nivel').value;
    const agente = document.getElementById('filtro-agente').value;
    let filtrados = logs;
    if (nivel !== 'all') filtrados = filtrados.filter(l => l.nivel === nivel);
    if (agente !== 'all') filtrados = filtrados.filter(l => l.agente === agente);
    const container = document.getElementById('historico-content');
    if (!filtrados.length) {
        container.innerHTML = '<em>Nenhum log encontrado.</em>';
        return;
    }
    container.innerHTML = filtrados.map(l => `
        <div style="margin-bottom:8px;padding:8px;border-radius:8px;background:${l.nivel==='error'?'#ffe5e5':l.nivel==='warning'?'#fffbe5':'#e5ffe5'};color:${l.nivel==='error'?'#b71c1c':l.nivel==='warning'?'#bfa600':'#1b5e20'};">
            <strong>[${l.nivel.toUpperCase()}]</strong> <span style="font-weight:bold;">${l.agente}</span> — ${l.mensagem}
            <span style="float:right;font-size:12px;opacity:0.7;">${l.timestamp}</span>
        </div>
    `).join('');
}

document.getElementById('filtro-nivel').addEventListener('change', () => {
    renderHistoricoLogs(window.allLogs || []);
});
document.getElementById('filtro-agente').addEventListener('change', () => {
    renderHistoricoLogs(window.allLogs || []);
});
document.getElementById('download-logs').addEventListener('click', () => {
    const logs = window.allLogs || [];
    const blob = new Blob([JSON.stringify(logs, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'logs.json';
    a.click();
    URL.revokeObjectURL(url);
});

function renderAgentesCards(agentes) {
    const container = document.getElementById('agentes-cards');
    container.innerHTML = '';
    agentes.forEach(agente => {
        const card = document.createElement('div');
        card.style.background = '#f8f9fa';
        card.style.borderRadius = '10px';
        card.style.boxShadow = '0 2px 8px #0001';
        card.style.padding = '12px';
        card.style.minWidth = '140px';
        card.style.display = 'flex';
        card.style.flexDirection = 'column';
        card.style.alignItems = 'center';
        card.style.gap = '8px';
        card.innerHTML = `
            <strong>${agente.nome}</strong>
            <span style="color:${agente.status==='ativo'?'green':agente.status==='erro'?'red':'orange'};font-weight:bold;">${agente.status}</span>
            <div>CPU: ${agente.cpu}% | RAM: ${agente.ram}%</div>
            <div>Tarefas/h: ${agente.tarefasHora}</div>
            <button onclick="window.location='/logs/${agente.nome}'">Ver Logs</button>
            <button onclick="window.location='/restart/${agente.nome}'">Reiniciar</button>
        `;
        container.appendChild(card);
    });
}

// Exemplo de inicialização visual
window.onload = function() {
    for (let i = 1; i <= 3; i++) {
        document.getElementById('monitor-content-' + i).innerHTML = '<em>Aguardando visualização...</em>';
    }
};

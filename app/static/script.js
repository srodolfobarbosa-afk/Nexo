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
        renderAgentesGauges(data.agentes);
    }
    if (data.type === 'financeiro') {
        document.getElementById('financeiro-graficos').innerHTML = data.graficos;
        renderGraficoFinanceiro(data);
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
        renderApiKeysManager(data.api_keys || []);
    }
function renderApiKeysManager(keys) {
    const list = document.getElementById('api-keys-list');
    list.innerHTML = '';
    keys.forEach((key, idx) => {
        const div = document.createElement('div');
        div.style.display = 'flex';
        div.style.alignItems = 'center';
        div.style.gap = '8px';
        div.innerHTML = `<span style="font-family:monospace;">${key}</span> <button style="padding:4px 8px;border-radius:6px;background:#e53935;color:white;border:none;cursor:pointer;" onclick="removerApiKey(${idx})">Revogar</button>`;
        list.appendChild(div);
    });
}

window.removerApiKey = function(idx) {
    ws.send(JSON.stringify({action:'remover_api_key',index:idx}));
}
document.getElementById('adicionar-api-key').addEventListener('click', () => {
    const novaKey = document.getElementById('nova-api-key').value.trim();
    if (novaKey) {
        ws.send(JSON.stringify({action:'adicionar_api_key',key:novaKey}));
        document.getElementById('nova-api-key').value = '';
    }
});
};
function renderAgentesGauges(agentes) {
    const container = document.getElementById('agentes-gauges');
    container.innerHTML = '';
    agentes.forEach(agente => {
        const gauge = document.createElement('div');
        gauge.style.display = 'flex';
        gauge.style.flexDirection = 'column';
        gauge.style.alignItems = 'center';
        gauge.innerHTML = `
            <span style="font-weight:bold;">${agente.nome}</span>
            <div style="width:60px;height:60px;border-radius:50%;background:#e5e5e5;display:flex;align-items:center;justify-content:center;position:relative;">
                <span style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:14px;">${agente.cpu}%</span>
                <svg width="60" height="60" style="position:absolute;top:0;left:0;">
                    <circle cx="30" cy="30" r="26" stroke="#667eea" stroke-width="6" fill="none" stroke-dasharray="${Math.round(2*Math.PI*26)}" stroke-dashoffset="${Math.round(2*Math.PI*26*(1-agente.cpu/100))}" />
                </svg>
            </div>
            <span style="font-size:12px;">RAM: ${agente.ram}%</span>
        `;
        container.appendChild(gauge);
    });
}

function renderGraficoFinanceiro(data) {
    const canvas = document.getElementById('grafico-financeiro');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0,0,canvas.width,canvas.height);
    // Exemplo: barras de receita, despesa, ROI
    const receita = 1000, despesa = 400, roi = 150;
    ctx.fillStyle = '#4CAF50';
    ctx.fillRect(30,80,60,-receita/20);
    ctx.fillStyle = '#e53935';
    ctx.fillRect(120,80,60,-despesa/10);
    ctx.fillStyle = '#667eea';
    ctx.fillRect(210,80,60,-roi);
    ctx.fillStyle = '#333';
    ctx.font = '14px Arial';
    ctx.fillText('Receita',30,110);
    ctx.fillText('Despesa',120,110);
    ctx.fillText('ROI',210,110);
}
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

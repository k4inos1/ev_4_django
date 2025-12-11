const app = {
    term: document.getElementById('sys_log'),

    log: (msg) => {
        app.term.innerHTML += `> ${msg}<br>`;
        app.term.scrollTop = app.term.scrollHeight;
    },

    ini_escan: async () => {
        app.log("INICIANDO NEURO_ESCAN...");
        try {
            const res = await fetch('/api/ot/neuro_escan/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto: "control critico", cat: 1 })
            });
            const data = await res.json();
            app.log(`RESULTADO: ${JSON.stringify(data)}`);
            update_viz("ALERT");
        } catch (e) {
            app.log(`ERROR: ${e}`);
        }
    },

    sim_data: async () => {
        app.log("INYECTANDO DATA SINTETICA...");
        // Simulación visual
        app.log("Desplegando 500 nodes...");
        setTimeout(() => update_viz("DATA"), 500);
    }
};

// Clock
setInterval(() => {
    document.getElementById('clk_sys').innerText = new Date().toISOString();
}, 100);

// Visualizer (Canvas)
const cv = document.getElementById('c_n');
const ctx = cv.getContext('2d');
const nodes = [];

function init_nodes() {
    for (let i = 0; i < 500; i++) {
        nodes.push({
            x: Math.random() * cv.width,
            y: Math.random() * cv.height,
            v: Math.random()
        });
    }
}

function update_viz(mode) {
    if (mode === "ALERT") {
        nodes.forEach(n => n.c = "#ff0000");
        setTimeout(() => nodes.forEach(n => n.c = "#00ff00"), 500);
    }
}

function loop() {
    ctx.fillStyle = "#001100";
    ctx.fillRect(0, 0, cv.width, cv.height);

    nodes.forEach(n => {
        ctx.fillStyle = n.c || "#00ff00";
        if (Math.random() > 0.99) n.x = Math.random() * cv.width;
        ctx.fillRect(n.x, n.y, 2, 2);
    });

    requestAnimationFrame(loop);
}

init_nodes();
loop();

// CLI Terminal Handler
const cli_input = document.getElementById('cli_in');
if (cli_input) {
    cli_input.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const cmd = cli_input.value.trim();
            if (!cmd) return;

            // Echo command
            app.log(`root@ev4:~# ${cmd}`);
            cli_input.value = '';

            // Handle clear locally
            if (cmd === 'clear') {
                app.term.innerHTML = '';
                return;
            }

            // Send to backend
            try {
                const res = await fetch('/api/terminal/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cmd })
                });
                const data = await res.json();
                app.log(data.out || 'Sin respuesta');
            } catch (err) {
                app.log(`ERROR: ${err}`);
            }
        }
    });

    // Auto-focus
    cli_input.focus();
}

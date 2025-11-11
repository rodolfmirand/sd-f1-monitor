const API_BASE = "http://localhost:8000";

const selectors = {
  rankingBody: document.querySelector("#rankingTable tbody"),
  alertsList: document.getElementById("alertsList"),
  carDetails: document.getElementById("carDetails"),
  refreshNowBtn: document.getElementById("refreshNow"),
  refreshIntervalSelect: document.getElementById("refreshInterval")
};

let refreshTimer = null;
let refreshInterval = parseInt(selectors.refreshIntervalSelect.value, 10);

selectors.refreshIntervalSelect.addEventListener("change", (e) => {
  refreshInterval = parseInt(e.target.value, 10);
  setupAutoRefresh();
});

selectors.refreshNowBtn.addEventListener("click", fetchAndRender);

async function fetchVeiculos() {
  try {
    const res = await fetch(`${API_BASE}/veiculos`);
    if (!res.ok) throw new Error("Erro /veiculos: " + res.status);
    return await res.json();
  } catch (err) {
    console.error(err);
    return null;
  }
}

async function fetchAlertas() {
  try {
    const res = await fetch(`${API_BASE}/alertas/pneus`);
    if (!res.ok) throw new Error("Erro /alertas/pneus: " + res.status);
    return await res.json();
  } catch (err) {
    console.error(err);
    return null;
  }
}

function formatTimestamp(ts) {
  const d = new Date(ts * 1000);
  return isNaN(d) ? "—" : d.toLocaleString();
}

function pressureClass(v) {
  if (v == null) return "muted";
  if (v < 85) return "red";
  if (v <= 90) return "orange";
  return "green";
}

function getWorstPressureClass(alertData) {
  const pressures = [
    alertData.front_left,
    alertData.front_right,
    alertData.rear_left,
    alertData.rear_right
  ];
  
  const minPressure = Math.min(...pressures.filter(p => p != null));

  return (minPressure === Infinity) ? "muted" : pressureClass(minPressure);
}


function clearChildren(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}

async function fetchAndRender() {
  selectors.rankingBody.innerHTML = `<tr><td colspan="8" class="muted">Carregando...</td></tr>`;
  selectors.alertsList.innerHTML = `<p class="muted">Carregando alertas...</p>`;

  const [veiculos, alertas] = await Promise.all([fetchVeiculos(), fetchAlertas()]);

  // veículos
  if (!veiculos) {
    selectors.rankingBody.innerHTML = `<tr><td colspan="8" class="muted">Erro ao buscar veículos</td></tr>`;
  } else {
    veiculos.sort((a, b) => {
      if (a.position == null && b.position == null) return 0;
      if (a.position == null) return 1;
      if (b.position == null) return -1;
      return a.position - b.position;
    });

    clearChildren(selectors.rankingBody);

    veiculos.forEach((v, idx) => {
      const tr = document.createElement("tr");
      tr.className = "clickable-row";
      tr.innerHTML = `
        <td>${v.position ?? idx + 1}</td>
        <td>${v.name || "—"}</td>
        <td>${v.team || "—"}</td>
        <td class="${pressureClass(v.front_left)}">${v.front_left?.toFixed(1) ?? "—"}</td>
        <td class="${pressureClass(v.front_right)}">${v.front_right?.toFixed(1) ?? "—"}</td>
        <td class="${pressureClass(v.rear_left)}">${v.rear_left?.toFixed(1) ?? "—"}</td>
        <td class="${pressureClass(v.rear_right)}">${v.rear_right?.toFixed(1) ?? "—"}</td>
      `;
      tr.addEventListener("click", () => showDetails(v));
      selectors.rankingBody.appendChild(tr);
    });
  }

  // alertas
  if (!alertas) {
    selectors.alertsList.innerHTML = `<p class="muted">Erro ao buscar alertas</p>`;
  } else if (alertas.length === 0) {
    selectors.alertsList.innerHTML = `<p class="muted">Nenhum alerta de pneus no momento ✅</p>`;
  } else {
    clearChildren(selectors.alertsList);
    alertas.forEach(a => {
      const div = document.createElement("div");
      div.className = "alert-item";

      const left = document.createElement("div");
      left.innerHTML = `
        <h4>${a.name} <span class="muted small">#${a.id}</span></h4> 
        <div class="muted small">${a.team || ""}</div>
      `;

      const right = document.createElement("div");
      right.className = "alert-values";
      const span = v => `<span class="${pressureClass(v)}">${v?.toFixed(1) ?? "—"}</span>`;
      right.innerHTML = `
        <div class="small">FL ${span(a.front_left)}</div>
        <div class="small">FR ${span(a.front_right)}</div>
        <div class="small">RL ${span(a.rear_left)}</div>
        <div class="small">RR ${span(a.rear_right)}</div>
      `;

      div.append(left, right);
      selectors.alertsList.appendChild(div);
    });
  }
}

function showDetails(v) {
  clearChildren(selectors.carDetails);

  const container = document.createElement("div");
  container.innerHTML = `
    <h3>${v.name} <span class="muted small">#${v.id} · ${v.team || ""}</span></h3>
    <div class="muted small">Última leitura: ${v.timestamp ? formatTimestamp(v.timestamp) : "—"}</div>
  `;

  const bars = document.createElement("div");
  bars.className = "detail-bars";

  const pneus = [
    { label: "Front Left", key: "front_left", short: "FL" },
    { label: "Front Right", key: "front_right", short: "FR" },
    { label: "Rear Left", key: "rear_left", short: "RL" },
    { label: "Rear Right", key: "rear_right", short: "RR" }
  ];

  pneus.forEach(p => {
    const val = v[p.key] ?? null;
    const cls = val == null ? "muted" : pressureClass(val);
    const percent = val == null ? 0 : Math.min(120, (val / 120) * 100);

    const div = document.createElement("div");
    div.className = "pneu";
    div.innerHTML = `
      <div class="label">${p.short} · ${p.label}</div>
      <div class="muted small">
        Pressão: <strong class="${cls}">${val != null ? `${val.toFixed(1)} PSI` : "—"}</strong>
      </div>
      <div class="progress"><i style="width:${percent}%"></i></div>
    `;
    bars.appendChild(div);
  });

  const actions = document.createElement("div");
  actions.style.marginTop = "10px";
  actions.innerHTML = `
    <button id="refreshCar" style="padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);background:transparent;color:var(--text);cursor:pointer">
      Recarregar dados do carro
    </button>
  `;

  container.append(bars, actions);
  selectors.carDetails.appendChild(container);

  document.getElementById("refreshCar").addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/veiculos/${v.id}`);
      if (!res.ok) throw new Error("Erro ao buscar veículo: " + res.status);
      const newV = await res.json();
      showDetails(newV);
      fetchAndRender();
    } catch (err) {
      console.error(err);
      alert("Erro ao recarregar veículo");
    }
  });
}

function setupAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  if (refreshInterval > 0) refreshTimer = setInterval(fetchAndRender, refreshInterval);
}

fetchAndRender();
setupAutoRefresh();
const API_BASE = "http://localhost:8000";

async function carregarVeiculos() {
  const res = await fetch(`${API_BASE}/veiculos`);
  const data = await res.json();
  const ul = document.getElementById("veiculos");
  ul.innerHTML = "";
  if (Array.isArray(data)) {
    data.forEach(v => {
      const li = document.createElement("li");
      li.textContent = `${v.id} - ${v.nome || v.modelo}`;
      ul.appendChild(li);
    });
  } else {
    ul.textContent = "Nenhum veículo encontrado";
  }
}

async function carregarAlertas() {
  const res = await fetch(`${API_BASE}/alertas/pneus`);
  const data = await res.json();
  const ul = document.getElementById("alertas");
  ul.innerHTML = "";
  if (Array.isArray(data)) {
    data.forEach(a => {
      const li = document.createElement("li");
      li.textContent = `${a.veiculo_id} - ${a.alerta}`;
      ul.appendChild(li);
    });
  } else {
    ul.textContent = "Nenhum alerta";
  }
}

window.addEventListener("DOMContentLoaded", () => {
  carregarVeiculos();
  carregarAlertas();
});

from fastapi import FastAPI, HTTPException
from repository import listar_veiculos, obter_veiculo, pneus_com_alerta

app = FastAPI(title="Servidor SVCP - Pneus F1")

@app.get("/veiculos")
def get_veiculos():
    return listar_veiculos()

@app.get("/veiculos/{idVeiculo}")
def get_veiculo_endpoint(idVeiculo: int):
    veiculo = obter_veiculo(idVeiculo)
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@app.get("/pneus/alertas")
def get_alertas():
    return pneus_com_alerta()

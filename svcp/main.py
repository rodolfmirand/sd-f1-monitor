from fastapi import FastAPI
from repository import listar_veiculos, obter_veiculo, pneus_com_alerta

app = FastAPI()

@app.get("/veiculos")
def get_veiculos():
    return listar_veiculos()

@app.get("/veiculos/{id}")
def get_veiculo(id: int):
    veiculo = obter_veiculo(id)
    return veiculo if veiculo else {"erro": "Veículo não encontrado"}

@app.get("/alertas/pneus")
def get_pneus_alerta():
    return pneus_com_alerta()

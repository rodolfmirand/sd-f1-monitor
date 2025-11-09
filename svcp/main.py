from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from repository import listar_veiculos, obter_veiculo, pneus_com_alerta
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

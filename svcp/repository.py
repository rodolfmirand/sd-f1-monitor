from pymongo import MongoClient
import os

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
DB_NAME = os.environ.get("MONGO_DB", "f1_db")

client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
db = client[DB_NAME]
colecao_veiculos = db["telemetria"]

def listar_veiculos():
    return list(colecao_veiculos.find({}, {"_id": 0, "id": 1, "name": 1, "team": 1}))

def obter_veiculo(idVeiculo: int):
    return colecao_veiculos.find_one({"id": idVeiculo}, {"_id": 0})

def pneus_com_alerta():
    query = {
        "$or": [
            {"front_left": {"$lt": 85}},
            {"front_right": {"$lt": 85}},
            {"rear_left": {"$lt": 85}},
            {"rear_right": {"$lt": 85}},
        ]
    }
    return list(colecao_veiculos.find(query, {
        "_id": 0,
        "id": 1,
        "name": 1,
        "team": 1,
        "front_left": 1,
        "front_right": 1,
        "rear_left": 1,
        "rear_right": 1
    }))

from pymongo import MongoClient
import os, time

MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))

DBS = [
    {"host": "mongo1", "db": "f1_db_1"},
    {"host": "mongo2", "db": "f1_db_2"},
    {"host": "mongo3", "db": "f1_db_3"},
]

clients = []
for conf in DBS:
    while True:
        try:
            uri = f"mongodb://{conf['host']}:{MONGO_PORT}/"
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")  # testa conexão
            clients.append(client[conf["db"]])
            print(f"[SVCP] Conectado ao banco {conf['db']} em {conf['host']}")
            break
        except Exception as e:
            print(f"[SVCP] Aguardando {conf['host']}... ({e})")
            time.sleep(2)

collections = [db["telemetria"] for db in clients]


def listar_veiculos():
    resultado = []
    for col in collections:
        resultado.extend(list(col.find({}, {"_id": 0, "id": 1, "name": 1, "team": 1})))
    return resultado


def obter_veiculo(idVeiculo: int):
    for col in collections:
        veiculo = col.find_one({"id": idVeiculo}, {"_id": 0})
        if veiculo:
            return veiculo
    return None


def pneus_com_alerta():
    query = {
        "$or": [
            {"front_left": {"$lt": 85}},
            {"front_right": {"$lt": 85}},
            {"rear_left": {"$lt": 85}},
            {"rear_right": {"$lt": 85}},
        ]
    }

    resultado = []
    for col in collections:
        resultado.extend(list(col.find(query, {
            "_id": 0, "id": 1, "name": 1, "team": 1,
            "front_left": 1, "front_right": 1,
            "rear_left": 1, "rear_right": 1
        })))
    return resultado

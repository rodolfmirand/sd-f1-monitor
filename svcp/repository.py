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
            client.admin.command("ping")
            clients.append(client[conf["db"]])
            print(f"[SVCP] Conectado ao banco {conf['db']} em {conf['host']}")
            break
        except Exception as e:
            print(f"[SVCP] Aguardando {conf['host']}... ({e})")
            time.sleep(2)

collections = [db["telemetria"] for db in clients]

def _get_latest_per_vehicle(col):
    pipeline = [
        {"$sort": {"id": 1, "timestamp": -1}},
        {
            "$group": {
                "_id": "$id",
                "latest": {"$first": "$$ROOT"}
            }
        },
        {"$replaceRoot": {"newRoot": "$latest"}},
        {"$project": {
            "_id": 0,
            "id": 1,
            "name": 1,
            "team": 1,
            "front_left": 1,
            "front_right": 1,
            "rear_left": 1,
            "rear_right": 1,
            "position": 1,
            "timestamp": 1
        }}
    ]
    return list(col.aggregate(pipeline))


def listar_veiculos():
    resultado = []
    for col in collections:
        resultado.extend(_get_latest_per_vehicle(col))
    return resultado


def obter_veiculo(idVeiculo: int):
    for col in collections:
        doc = (
            col.find({"id": idVeiculo}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(1)
        )
        doc = list(doc)
        if doc:
            return doc[0]
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
        latest_docs = _get_latest_per_vehicle(col)
        for v in latest_docs:
            if (
                v.get("front_left", 999) < 85
                or v.get("front_right", 999) < 85
                or v.get("rear_left", 999) < 85
                or v.get("rear_right", 999) < 85
            ):
                resultado.append({
                    "id": v.get("id"),
                    "name": v.get("name"),
                    "team": v.get("team"),
                    "front_left": v.get("front_left"),
                    "front_right": v.get("front_right"),
                    "rear_left": v.get("rear_left"),
                    "rear_right": v.get("rear_right"),
                })
    return resultado

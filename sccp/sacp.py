import paho.mqtt.client as mqtt
import json, time, datetime, os
from pymongo import MongoClient
from models import CarData

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
DB_NAME = os.environ.get("MONGO_DB", "f1_db")

MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt-broker")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))

client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/", serverSelectionTimeoutMS=5000)

while True:
    try:
        client.admin.command("ping")
        print(f"[SSACP] Conectado ao MongoDB em {MONGO_HOST}:{MONGO_PORT}")
        break
    except Exception:
        print("[SSACP] Aguardando MongoDB ficar pronto...")
        time.sleep(2)

db = client[DB_NAME]
collection = db["telemetria"]

ssacp_id = int(DB_NAME.split("_")[-1])

def msg(c, u, m):
    d = json.loads(m.payload.decode())
    obj = CarData.from_dict(d)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    collection.insert_one(obj.to_dict())
    print(f"[{ts}] [SSACP {ssacp_id}] Dados armazenados: {obj.name} ({obj.team}) posição {obj.position:.2f}")

c = mqtt.Client(f"sacp{ssacp_id}")

while True:
    try:
        c.connect(MQTT_HOST, MQTT_PORT, 60)
        print(f"[SSACP {ssacp_id}] Conectado ao broker!")
        break
    except:
        print(f"[SSACP {ssacp_id}] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

topic = f"f1/ssacp/{ssacp_id}"
c.subscribe(topic)
print(f"[SSACP {ssacp_id}] Escutando tópico: {topic}")

c.on_message = msg
print(f"[SSACP {ssacp_id}] Aguardando dados...")
c.loop_forever()

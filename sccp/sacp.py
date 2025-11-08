import paho.mqtt.client as mqtt
import json, time, datetime, os
from pymongo import MongoClient
from models import CarData

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
DB_NAME = os.environ.get("MONGO_DB", "f1_db")

MQTT_HOST = os.environ.get("MQTT_HOST", "mqtt-broker")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))

client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
db = client[DB_NAME]
collection = db["telemetria"]

def msg(c, u, m):
    d = json.loads(m.payload.decode())
    obj = CarData.from_dict(d)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    collection.insert_one(obj.to_dict())

    print(f"[{ts}] [SSACP] Dados armazenados: {obj.name} ({obj.team}) posição {obj.position:.2f}")

c = mqtt.Client("sacp")

while True:
    try:
        c.connect("mqtt-broker", 1883, 60)
        print("[SSACP] Conectado ao broker!")
        break
    except:
        print("[SSACP] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

c.on_message = msg
c.subscribe("f1/isccp/obj")

print("[SSACP] Aguardando dados...")
c.loop_forever()

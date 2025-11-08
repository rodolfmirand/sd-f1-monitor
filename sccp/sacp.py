import paho.mqtt.client as mqtt
import json, time, datetime
from pymongo import MongoClient
from models import CarData

mongo = MongoClient("mongodb://mongo:27017/")
db = mongo["f1_db"]
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

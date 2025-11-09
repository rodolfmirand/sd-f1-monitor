import paho.mqtt.client as mqtt
import json, time, datetime, random
from models import CarData

INSTANCE_ID = random.randint(1000, 9999)
ssacp_ids = [1, 2, 3]

def msg(c, u, m):
    d = json.loads(m.payload.decode())
    obj = CarData(**d)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    
    destino = random.choice(ssacp_ids)
    print(f"[{ts}] ISCCP-{INSTANCE_ID} enviando {obj.name} -> SSACP {destino}")
    
    c.publish(f"f1/ssacp/{destino}", json.dumps(obj.to_dict()))

c = mqtt.Client(f"isccp{INSTANCE_ID}")

while True:
    try:
        c.connect("mqtt-broker", 1883, 60)
        print(f"[ISCCP-{INSTANCE_ID}] Conectado ao broker!")
        break
    except:
        print(f"[ISCCP-{INSTANCE_ID}] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

c.on_message = msg
c.subscribe("f1/carros/#")

print(f"[ISCCP-{INSTANCE_ID}] Aguardando mensagens...")
c.loop_forever()
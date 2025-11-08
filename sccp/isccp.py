import paho.mqtt.client as mqtt
import json, time, datetime
from models import CarData

def msg(c, u, m):
    d = json.loads(m.payload.decode())
    obj = CarData(**d)
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] Enviando objeto de {obj.name} ({obj.team}) para o SSACP")
    c.publish("f1/isccp/obj", json.dumps(obj.to_dict()))

c = mqtt.Client("isccp")
while True:
    try:
        c.connect("mqtt-broker", 1883, 60)
        print("[ISCCP] Conectado ao broker!")
        break
    except:
        print("[ISCCP] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

c.on_message = msg
c.subscribe("f1/carros/#")

print("[ISCCP] Aguardando mensagens...")
c.loop_forever()
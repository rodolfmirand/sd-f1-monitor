import paho.mqtt.client as mqtt
import json, time, datetime

def msg(c, u, m):
    d = json.loads(m.payload.decode())
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] Recebido de {m.topic}: {d}")
    c.publish("f1/isccp/dados", json.dumps(d))

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
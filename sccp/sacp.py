import paho.mqtt.client as mqtt
import json, time, datetime

dados = []

def msg(c, u, m):
    d = json.loads(m.payload.decode())
    dados.append(d)
    ts = datetime.datetime.now().strftime("%H:%M:%S")

    avg_temp = sum([
        d["front_left"],
        d["front_right"],
        d["rear_left"],
        d["rear_right"]
    ]) / 4

    print(f"[{ts}] [SACP] Dados recebidos de {d['name']} ({d['team']}): média pneus = {avg_temp:.2f}")

c = mqtt.Client("sacp")

while True:
    try:
        c.connect("mqtt-broker", 1883, 60)
        print("[SACP] Conectado ao broker!")
        break
    except:
        print("[SACP] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

c.on_message = msg
c.subscribe("f1/isccp/dados")

print("[SACP] Aguardando dados...")
c.loop_forever()

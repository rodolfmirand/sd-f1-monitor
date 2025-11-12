import paho.mqtt.client as mqtt
import json, time, datetime, socket
from models import CarData

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("id-server", 5000))
        s.sendall(b"isccp")
        location_id = int(s.recv(1024).decode())
        s.close()
        break
    except Exception:
        print("[ISCCP] Servidor de ID ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

print(f"[ISCCP] Instância iniciada para LOCALIZAÇÃO {location_id}")

client = mqtt.Client(f"isccp-{location_id}")
while True:
    try:
        client.connect("mqtt-broker", 1883, 60)
        print(f"[ISCCP {location_id}] Conectado ao broker!")
        break
    except Exception:
        print(f"[ISCCP {location_id}] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

SSACP_COUNT = 3
def on_message(c, userdata, msg):
    try:
        d = json.loads(msg.payload.decode())
        obj = CarData(**d)
    except Exception as e:
        print(f"[ISCCP {location_id}] Erro ao desserializar mensagem: {e}")
        return

    ts = datetime.datetime.now().strftime("%H:%M:%S")
    ssacp_target = (obj.id - 1) % SSACP_COUNT + 1
    topic = f"f1/ssacp/{ssacp_target}"

    print(f"[{ts}] [ISCCP {location_id}] Recebeu {obj.name} (car {obj.id}) — enviando para SSACP {ssacp_target}")
    client.publish(topic, json.dumps(obj.to_dict()))

client.on_message = on_message

topic = f"f1/isccp/{location_id}"
client.subscribe(topic)
print(f"[ISCCP {location_id}] Inscrito no tópico de localização: {topic}")

print(f"[ISCCP {location_id}] Aguardando mensagens...")
client.loop_forever()
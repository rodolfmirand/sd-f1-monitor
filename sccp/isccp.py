import paho.mqtt.client as mqtt
import json, time, datetime, socket
from models import CarData

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("id-server", 5000))
        s.sendall(b"isccp")
        isccp_id = int(s.recv(1024).decode())
        s.close()
        break
    except Exception:
        print("[ISCCP] Servidor de ID ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

print(f"[ISCCP] Instância iniciada com ID {isccp_id}")

client = mqtt.Client(f"isccp-{isccp_id}")
while True:
    try:
        client.connect("mqtt-broker", 1883, 60)
        print(f"[ISCCP-{isccp_id}] Conectado ao broker!")
        break
    except Exception:
        print(f"[ISCCP-{isccp_id}] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

TOTAL_CARROS = 24
TOTAL_ISCCP = 15

# Distribuição fixa: primeiros 9 ISCCP têm 2 carros, próximos 6 têm 1 carro.
index = isccp_id - 1000

carros_por_isccp = []
for i in range(TOTAL_ISCCP):
    if i < 9:
        carros_por_isccp.append(2)
    else:
        carros_por_isccp.append(1)

if index < 0 or index >= TOTAL_ISCCP:
    print(f"[ISCCP-{isccp_id}] ID fora do intervalo esperado. Nenhum carro atribuído.")
    assigned = []
else:
    start = 1 + sum(carros_por_isccp[:index])
    count = carros_por_isccp[index]
    end = start + count - 1

    if start > TOTAL_CARROS:
        assigned = []
    else:
        end = min(end, TOTAL_CARROS)
        assigned = list(range(start, end + 1))

print(f"[ISCCP-{isccp_id}] Escutando carros: {assigned}")

# Ao receber dados de um carro, repassa para um SSACP específico ---
SSACP_COUNT = 3
def on_message(c, userdata, msg):
    try:
        d = json.loads(msg.payload.decode())
        obj = CarData(**d)
    except Exception as e:
        print(f"[ISCCP-{isccp_id}] Erro ao desserializar mensagem: {e}")
        return

    ts = datetime.datetime.now().strftime("%H:%M:%S")
    # escolha de SSACP: round-robin por id do carro (1..3)
    ssacp_target = (obj.id - 1) % SSACP_COUNT + 1
    topic = f"f1/ssacp/{ssacp_target}"

    print(f"[{ts}] [ISCCP-{isccp_id}] Recebeu {obj.name} (car {obj.id}) — enviando para SSACP {ssacp_target} no tópico {topic}")
    client.publish(topic, json.dumps(obj.to_dict()))

# Assina os tópicos dos carros atribuídos
client.on_message = on_message
for cid in assigned:
    topic = f"f1/carros/{cid}"
    client.subscribe(topic)
    print(f"[ISCCP-{isccp_id}] Subscribed to {topic}")

print(f"[ISCCP-{isccp_id}] Aguardando mensagens...")
client.loop_forever()

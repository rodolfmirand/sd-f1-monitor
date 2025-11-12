import paho.mqtt.client as mqtt
import random, json, time, string, socket

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("id-server", 5000))
        s.sendall(b"car")
        id = int(s.recv(1024).decode())
        s.close()
        break
    except:
        print("[CAR] Servidor de ID ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

print(f"[CAR] Recebi ID = {id}")

team = random.choice([
    "Red Bull", "Ferrari", "Mercedes", "McLaren",
    "Aston Martin", "Williams", "Alpine", "Haas",
])
name = ''.join(random.choices(string.ascii_uppercase, k=3)) + str(random.randint(1,99))

c = mqtt.Client(f"car{id}")

time.sleep(id * 0.5) 

while True:
    try:
        c.connect("mqtt-broker", 1883, 60)
        break
    except:
        print("[CAR] Broker ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

def get_position(car_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("position-server", 5050))
        s.sendall(str(car_id).encode())
        pos = int(s.recv(1024).decode())
        s.close()
        return pos
    except Exception as e:
        print(f"[CAR {car_id}] Erro ao obter posição de corrida: {e}")
        return car_id 

TOTAL_ISCCP_LOCATIONS = 15
current_location = random.randint(1, TOTAL_ISCCP_LOCATIONS)

print(f"[CAR {id}] Iniciando no ISCCP {current_location}...")

while True:
    race_position = get_position(id)

    d = {
        "id": id,
        "name": name,
        "team": team,
        "front_left": round(random.uniform(80, 100), 2),
        "front_right": round(random.uniform(80, 100), 2),
        "rear_left": round(random.uniform(80, 100), 2),
        "rear_right": round(random.uniform(80, 100), 2),
        "position": race_position,
        "timestamp": time.time()
    }

    topic = f"f1/isccp/{current_location}"
    c.publish(topic, json.dumps(d))
    print(f"[CAR {id}] Chegou ao ISCCP {current_location} (Pos: {race_position}º). Enviando dados...")

    time.sleep(random.uniform(2, 5))

    current_location += 1
    if current_location > TOTAL_ISCCP_LOCATIONS:
        current_location = 1
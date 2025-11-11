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

position = id

def get_position(car_id):
    """Solicita posição atual ao position-server"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("position-server", 5050))
        s.sendall(str(car_id).encode())
        pos = int(s.recv(1024).decode())
        s.close()
        return pos
    except Exception as e:
        print(f"[CAR {car_id}] Erro ao obter posição: {e}")
        return car_id 

t = f"f1/carros/{id}"
while True:
    if random.random() < 0.3:
        position += random.choice([-1, 1])

    position = get_position(id)

    d = {
        "id": id,
        "name": name,
        "team": team,
        "front_left": round(random.uniform(80, 100), 2),
        "front_right": round(random.uniform(80, 100), 2),
        "rear_left": round(random.uniform(80, 100), 2),
        "rear_right": round(random.uniform(80, 100), 2),
        "position": position,
        "timestamp": time.time()
    }

    c.publish(t, json.dumps(d))
    print(f"[CAR {id}] {d}")

    time.sleep(2 + id * 0.1)
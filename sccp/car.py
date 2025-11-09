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

team = random.choice(["Red Bull", "Ferrari", "Mercedes", "McLaren", "Aston Martin", "Williams"])
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

t = f"f1/carros/{id}"
while True:
    d = {
        "id": id, "name": name, "team": team,
        "front_left": round(random.uniform(80, 100), 2),
        "front_right": round(random.uniform(80, 100), 2),
        "rear_left": round(random.uniform(80, 100), 2),
        "rear_right": round(random.uniform(80, 100), 2),
        "position": round(random.uniform(25, 30), 2),
        "timestamp": time.time()
    }
    c.publish(t, json.dumps(d))
    print(f"[CAR {id}] {d}")
    time.sleep(2 + id * 0.1)  # publica em tempos levemente diferentes

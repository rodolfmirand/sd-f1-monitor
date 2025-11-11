import socket
import threading
import random
import time

HOST = ""
PORT = 5050

positions = list(range(1, 25))
lock = threading.Lock()

CHANGE_INTERVAL = 3
CHANGE_PROBABILITY = 0.25


def handle_client(conn, addr):
    """Retorna a posição atual do carro solicitante"""
    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return

        car_id = int(data.decode().strip())
        if not (1 <= car_id <= len(positions)):
            conn.sendall(b"ERRO: ID invalido")
            conn.close()
            return

        with lock:
            position = positions[car_id - 1]
        conn.sendall(str(position).encode())

        print(f"[POS SERVER] Enviado posicao {position} para CARRO {car_id} ({addr})")

    except Exception as e:
        print(f"[POS SERVER] Erro com {addr}: {e}")
    finally:
        conn.close()


def simulate_race():
    """Thread que ocasionalmente troca posições entre carros"""
    global positions
    while True:
        time.sleep(CHANGE_INTERVAL)
        with lock:
            if random.random() < CHANGE_PROBABILITY:
                i, j = random.sample(range(len(positions)), 2)
                positions[i], positions[j] = positions[j], positions[i]
                print(f"[POS SERVER] TROCA! Carro {i+1} ↔ Carro {j+1}")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"[POS SERVER] Servidor de posicoes rodando na porta {PORT}...")

threading.Thread(target=simulate_race, daemon=True).start()

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

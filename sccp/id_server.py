import socket
import threading

HOST = ''
PORT = 5000

next_car_id = 1
next_isccp_id = 1000
lock = threading.Lock()

def handle_client(conn, addr):
    global next_car_id, next_isccp_id
    try:
        tipo_raw = conn.recv(1024)
        if not tipo_raw:
            conn.close()
            return

        tipo = tipo_raw.decode().strip().lower()

        with lock:
            if tipo == "car":
                car_id = next_car_id
                next_car_id += 1
                conn.sendall(str(car_id).encode())
                print(f"[ID SERVER] Enviado ID de CARRO {car_id} para {addr}")

            elif tipo == "isccp":
                isccp_id = next_isccp_id
                next_isccp_id += 1
                conn.sendall(str(isccp_id).encode())
                print(f"[ID SERVER] Enviado ID de ISCCP {isccp_id} para {addr}")

            else:
                if tipo:
                    conn.sendall(b"ERRO: tipo invalido (use 'car' ou 'isccp')")
                    print(f"[ID SERVER] Tipo de cliente desconhecido: '{tipo}' ({addr})")

    except Exception as e:
        print(f"[ID SERVER] Erro ao lidar com {addr}: {e}")
    finally:
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"[ID SERVER] Servidor de IDs rodando na porta {PORT}...")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()

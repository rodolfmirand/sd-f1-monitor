import socket
import threading

HOST = ''
PORT = 5000
next_id = 1
lock = threading.Lock()

def handle_client(conn, addr):
    global next_id
    with lock:
        car_id = next_id
        next_id += 1
    conn.sendall(str(car_id).encode())
    conn.close()
    print(f"[ID SERVER] Enviado ID {car_id} para {addr}")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"[ID SERVER] Aguardando conexões na porta {PORT}...")

while True:
    conn, addr = s.accept()
    threading.Thread(target=handle_client, args=(conn, addr)).start()
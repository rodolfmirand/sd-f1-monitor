import paho.mqtt.client as mqtt
import json, time, datetime, socket, os
import grpc
import f1_pb2
import f1_pb2_grpc

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

print(f"[ISCCP] Instância iniciada para localização {location_id}")

SSACP_COUNT = 3
GRPC_PORT = int(os.environ.get("GRPC_PORT", 50051))
ssacp_stubs = {}

for i in range(1, SSACP_COUNT + 1):
    server_name = f'ssacp-{i}'
    server_address = f'{server_name}:{GRPC_PORT}'
    
    while True:
        try:
            channel = grpc.insecure_channel(server_address)
            grpc.channel_ready_future(channel).result(timeout=5)
            ssacp_stubs[i] = f1_pb2_grpc.SACPServiceStub(channel)
            print(f"[ISCCP {location_id}] Conectado ao gRPC do SSACP {i} em {server_address}")
            break
        except grpc.FutureTimeoutError:
            print(f"[ISCCP {location_id}] SSACP {i} não disponível em {server_address}. Tentando novamente em 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[ISCCP {location_id}] Erro ao conectar ao SSACP {i}: {e}. Tentando novamente em 5s...")
            time.sleep(5)

client = mqtt.Client(f"isccp-{location_id}")
while True:
    try:
        client.connect("mqtt-broker", 1883, 60)
        print(f"[ISCCP {location_id}] Conectado ao broker MQTT!")
        break
    except Exception:
        print(f"[ISCCP {location_id}] Broker MQTT ainda não disponível... tentando novamente em 2s")
        time.sleep(2)

def on_message(c, userdata, msg):
    try:
        d = json.loads(msg.payload.decode())
    except Exception as e:
        print(f"[ISCCP {location_id}] Erro ao desserializar mensagem: {e}")
        return

    ts = datetime.datetime.now().strftime("%H:%M:%S")

    ssacp_target = (d['id'] - 1) % SSACP_COUNT + 1
    
    try:
        stub = ssacp_stubs[ssacp_target]
        
        telemetry_request = f1_pb2.CarTelemetry(
            id=d['id'],
            name=d['name'],
            team=d['team'],
            front_left=d['front_left'],
            front_right=d['front_right'],
            rear_left=d['rear_left'],
            rear_right=d['rear_right'],
            position=d['position'],
            timestamp=d['timestamp']
        )

        response = stub.StoreTelemetry(telemetry_request)

        if response.success:
            print(f"[{ts}] [ISCCP {location_id}] Recebeu {d['name']} (car {d['id']}) — RPC enviado para SSACP {ssacp_target}")
        else:
            print(f"[{ts}] [ISCCP {location_id}] SSACP {ssacp_target} reportou falha ao salvar dados.")
            
    except grpc.RpcError as e:
        print(f"[{ts}] [ISCCP {location_id}] Erro ao enviar RPC para SSACP {ssacp_target}: {e.details()}")
    except Exception as e:
        print(f"[{ts}] [ISCCP {location_id}] Erro inesperado no gRPC: {e}")


client.on_message = on_message

topic = f"f1/isccp/{location_id}"
client.subscribe(topic)
print(f"[ISCCP {location_id}] Inscrito no tópico de localização MQTT: {topic}")

print(f"[ISCCP {location_id}] Aguardando mensagens...")
client.loop_forever()
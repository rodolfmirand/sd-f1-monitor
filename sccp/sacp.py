import grpc
from concurrent import futures
import time, datetime, os
from pymongo import MongoClient
import f1_pb2
import f1_pb2_grpc

MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
DB_NAME = os.environ.get("MONGO_DB", "f1_db")
GRPC_PORT = int(os.environ.get("GRPC_PORT", 50051))

client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/", serverSelectionTimeoutMS=5000)
while True:
    try:
        client.admin.command("ping")
        print(f"[SSACP] Conectado ao MongoDB em {MONGO_HOST}:{MONGO_PORT}")
        break
    except Exception:
        print("[SSACP] Aguardando MongoDB ficar pronto...")
        time.sleep(2)

db = client[DB_NAME]
collection = db["telemetria"]

try:
    ssacp_id = int(DB_NAME.split("_")[-1])
except:
    ssacp_id = 1

class SACPServiceServicer(f1_pb2_grpc.SACPServiceServicer):

    def StoreTelemetry(self, request, context):
        obj_dict = {
            "id": request.id,
            "name": request.name,
            "team": request.team,
            "front_left": request.front_left,
            "front_right": request.front_right,
            "rear_left": request.rear_left,
            "rear_right": request.rear_right,
            "position": request.position,
            "timestamp": request.timestamp
        }

        try:
            collection.insert_one(obj_dict)
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] [SSACP {ssacp_id}] Dados armazenados: {request.name} ({request.team}) posição {request.position}")
            
            return f1_pb2.StoreReply(success=True)
            
        except Exception as e:
            print(f"[SSACP {ssacp_id}] Erro ao inserir no BD: {e}")
            return f1_pb2.StoreReply(success=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    f1_pb2_grpc.add_SACPServiceServicer_to_server(SACPServiceServicer(), server)
    
    server_address = f'[::]:{GRPC_PORT}'
    server.add_insecure_port(server_address)
    
    print(f"[SSACP {ssacp_id}] Servidor gRPC iniciado. Escutando em {server_address}")
    server.start()
    server.wait_for_termination()

serve()
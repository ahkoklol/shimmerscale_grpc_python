from concurrent import futures
import grpc
from service.stock_service import StockService   # import the class

from service.stock import stock_service_pb2_grpc  # only for adding servicer

def serve():
    print("Starting gRPC server…")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    stock_service_pb2_grpc.add_StockServiceServicer_to_server(StockService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051, running…")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nServer stopped by user")

if __name__ == "__main__":
    serve()

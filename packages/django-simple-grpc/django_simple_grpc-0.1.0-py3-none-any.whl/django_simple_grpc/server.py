from concurrent import futures
import grpc
from django.conf import settings


class GRPCServer:
    """
    Simplified gRPC server for Django.

    Usage:
        from my_proto import add_MyServiceServicer_to_server
        from myapp.grpc_service import MyServiceImpl

        server = GRPCServer(add_MyServiceServicer_to_server, MyServiceImpl())
        server.start()
    """

    def __init__(self, service_register_function, service_implementation, max_workers=10):
        self.port = getattr(settings, "GRPC_SERVER_PORT", 50051)
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))

        # Register the service
        service_register_function(service_implementation, self.server)

        # Bind to port
        self.server.add_insecure_port(f"[::]:{self.port}")

    def start(self):
        print(f"Starting gRPC server on port {self.port}...")
        self.server.start()
        self.server.wait_for_termination()

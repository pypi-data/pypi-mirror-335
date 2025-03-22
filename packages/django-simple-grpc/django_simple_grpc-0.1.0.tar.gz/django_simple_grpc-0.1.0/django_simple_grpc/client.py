import grpc
from django.conf import settings
from typing import Any, Optional


class GRPCClient:
    """
    Simplified gRPC client for Django apps.

    Example:
        client = GRPCClient(MyServiceStub)
        response = client.call("MyMethod", MyRequest(name="Hello"))
    """

    def __init__(self, stub_class: Any, service_address: Optional[str] = None):
        self.address = service_address or getattr(settings, "GRPC_SERVER_ADDRESS", "localhost:50051")
        self.channel = grpc.insecure_channel(self.address)
        self.stub = stub_class(self.channel)

    def call(self, method_name: str, request):
        method = getattr(self.stub, method_name, None)
        if not method:
            raise AttributeError(f"Method '{method_name}' not found in '{self.stub.__class__.__name__}'")
        return method(request)

from django.core.management.base import BaseCommand
from django.conf import settings
from importlib import import_module
from django_simple_grpc.server import GRPCServer

class Command(BaseCommand):
    help = "Run the gRPC server"

    def handle(self, *args, **options):
        # Expect these paths in Django settings:
        # GRPC_SERVICE_REGISTER = 'myapp.grpc_generated.add_MyServiceServicer_to_server'
        # GRPC_SERVICE_IMPL = 'myapp.grpc_service.MyServiceImpl'

        service_register_path = getattr(settings, "GRPC_SERVICE_REGISTER", None)
        service_impl_path = getattr(settings, "GRPC_SERVICE_IMPL", None)

        if not service_register_path or not service_impl_path:
            self.stderr.write("Missing GRPC_SERVICE_REGISTER or GRPC_SERVICE_IMPL in settings.py")
            return

        # Dynamically import
        reg_module_path, reg_func = service_register_path.rsplit(".", 1)
        impl_module_path, impl_class = service_impl_path.rsplit(".", 1)

        register_func = getattr(import_module(reg_module_path), reg_func)
        impl_class_obj = getattr(import_module(impl_module_path), impl_class)

        server = GRPCServer(register_func, impl_class_obj())
        server.start()

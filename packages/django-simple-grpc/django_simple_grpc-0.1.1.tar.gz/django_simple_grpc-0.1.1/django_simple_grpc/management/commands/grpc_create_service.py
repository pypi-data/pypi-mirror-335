import os
from django.core.management.base import BaseCommand

PROTO_TEMPLATE = """syntax = "proto3";

package {package_name};

service {service_name} {{
  rpc SayHello (HelloRequest) returns (HelloReply);
}}

message HelloRequest {{
  string name = 1;
}}

message HelloReply {{
  string message = 1;
}}
"""

class Command(BaseCommand):
    help = "Create a boilerplate .proto file for a new gRPC service"

    def add_arguments(self, parser):
        parser.add_argument("service_name", type=str, help="Name of the gRPC service")

    def handle(self, *args, **options):
        service_name = options["service_name"]
        proto_dir = os.path.join(os.getcwd(), "protos")
        os.makedirs(proto_dir, exist_ok=True)

        file_name = service_name.lower() + ".proto"
        file_path = os.path.join(proto_dir, file_name)

        if os.path.exists(file_path):
            self.stderr.write(f"⚠️ {file_name} already exists.")
            return

        content = PROTO_TEMPLATE.format(
            package_name=service_name.lower(),
            service_name=service_name
        )

        with open(file_path, "w") as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"✅ Created: {file_path}"))

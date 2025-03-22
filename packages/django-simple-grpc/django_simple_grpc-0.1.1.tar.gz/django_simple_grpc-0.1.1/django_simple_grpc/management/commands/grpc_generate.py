import os
import subprocess
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compile all .proto files into gRPC Python code"

    def handle(self, *args, **kwargs):
        proto_dir = os.path.join(os.getcwd(), "protos")
        out_dir = os.path.join(os.getcwd(), "grpc_generated")
        os.makedirs(out_dir, exist_ok=True)

        proto_files = [f for f in os.listdir(proto_dir) if f.endswith(".proto")]

        if not proto_files:
            self.stderr.write("⚠️ No .proto files found in /protos")
            return

        for proto_file in proto_files:
            full_path = os.path.join(proto_dir, proto_file)
            cmd = [
                "python", "-m", "grpc_tools.protoc",
                f"--proto_path={proto_dir}",
                f"--python_out={out_dir}",
                f"--grpc_python_out={out_dir}",
                proto_file
            ]
            subprocess.run(cmd, check=True)
            self.stdout.write(self.style.SUCCESS(f"✅ Compiled: {proto_file} → grpc_generated/"))

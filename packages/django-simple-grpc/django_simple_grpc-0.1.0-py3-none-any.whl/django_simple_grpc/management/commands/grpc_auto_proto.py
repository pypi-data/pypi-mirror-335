import os
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel

PROTO_HEADER = """syntax = "proto3";

package {package};

import "google/protobuf/empty.proto";

"""

SERVICE_TEMPLATE = """
service {service_name} {{
  rpc List{model_name}s (google.protobuf.Empty) returns ({model_name}List);
}}
"""

MESSAGE_TEMPLATE = """
message {model_name} {{
{fields}
}}

message {model_name}List {{
  repeated {model_name} items = 1;
}}
"""

class Command(BaseCommand):
    help = "Auto-generate .proto file from Django model"

    def add_arguments(self, parser):
        parser.add_argument("app_label", type=str, help="App label (e.g. book)")
        parser.add_argument("service_name", type=str, help="gRPC service name (e.g. BookService)")

    def handle(self, *args, **options):
        app_label = options["app_label"]
        service_name = options["service_name"]

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            self.stderr.write(self.style.ERROR(f"App '{app_label}' not found."))
            return

        model_name = service_name.replace("Service", "")
        model = app_config.get_model(model_name)

        if not model:
            self.stderr.write(self.style.ERROR(f"Model '{model_name}' not found in app '{app_label}'"))
            return

        field_map = {
            "AutoField": "int32",
            "BigAutoField": "int64",
            "CharField": "string",
            "TextField": "string",
            "IntegerField": "int32",
            "BigIntegerField": "int64",
            "FloatField": "float",
            "BooleanField": "bool",
        }

        field_lines = []
        fields = [
            f for f in model._meta.get_fields()
            if not isinstance(f, (ManyToOneRel, ManyToManyRel))
        ]

        i = 1
        for field in fields:
            field_type = field.__class__.__name__
            proto_type = field_map.get(field_type, "string")  # fallback to string
            field_lines.append(f"  {proto_type} {field.name} = {i};")
            i += 1

        fields_proto = "\n".join(field_lines)
        content = (
            PROTO_HEADER.format(package=app_label)
            + SERVICE_TEMPLATE.format(service_name=service_name, model_name=model_name)
            + MESSAGE_TEMPLATE.format(model_name=model_name, fields=fields_proto)
        )

        os.makedirs("protos", exist_ok=True)
        filename = os.path.join("protos", f"{model_name.lower()}.proto")
        with open(filename, "w") as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"✅ Generated: {filename}"))

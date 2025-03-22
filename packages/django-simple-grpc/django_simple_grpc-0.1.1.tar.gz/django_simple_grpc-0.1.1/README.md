# django-simple-grpc

**django-simple-grpc** is a developer-friendly Django package that makes using gRPC in Django **simple, fast, and automatic**.

It supports both server and client code, and includes powerful Django management commands for generating `.proto` files and gRPC services from your existing models.

---

## 🚀 Features

- ✅ Auto-generate `.proto` files from Django models  
- ✅ Compile `.proto` files to Python gRPC stubs using `grpcio-tools`  
- ✅ Run gRPC servers using a clean `run_grpc` command  
- ✅ Build gRPC clients easily with `GRPCClient`  
- ✅ Works with Django 3.2+ (up to 5.x)  
- ✅ Compatible with Python 3.7–3.12  

---

## 📦 Installation

```bash
pip install django-simple-grpc
```

---

## ⚙️ Setup in Django

Add to your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django_simple_grpc",
]
```

Then add the gRPC configuration:

```python
# gRPC settings
GRPC_SERVER_PORT = 50051
GRPC_SERVER_ADDRESS = "localhost:50051"

# Replace <your_app> and <YourServiceName> with your actual values
GRPC_SERVICE_REGISTER = "grpc_generated.<your_app>_pb2_grpc.add_<YourServiceName>Servicer_to_server"
GRPC_SERVICE_IMPL = "<your_app>.grpc_service.<YourServiceName>Servicer"
```

🔁 Example if your app is called `store` and your service is `ProductService`:

```python
GRPC_SERVICE_REGISTER = "grpc_generated.store_pb2_grpc.add_ProductServiceServicer_to_server"
GRPC_SERVICE_IMPL = "store.grpc_service.ProductServiceServicer"
```

---

## 🛠️ Basic Usage

### 1. Generate `.proto` file from your model

```bash
python manage.py grpc_auto_proto <app_name> <ServiceName>
```

Example:

```bash
python manage.py grpc_auto_proto book BookService
```

---

### 2. Compile the `.proto` into Python gRPC code

```bash
python manage.py grpc_generate
```

This creates Python files in `grpc_generated/`.

---

### 3. Implement the service logic

```python
# book/grpc_service.py

from grpc_generated import book_pb2, book_pb2_grpc
from book.models import Book
from google.protobuf import empty_pb2

class BookServiceServicer(book_pb2_grpc.BookServiceServicer):
    def ListBooks(self, request, context):
        books = Book.objects.all()
        return book_pb2.BookList(
            items=[
                book_pb2.Book(id=b.id, title=b.title, author=b.author)
                for b in books
            ]
        )
```

---

### 4. Run the gRPC server

```bash
python manage.py run_grpc
```

---

## 🛰️ Client Example

Create a simple test script like `test_client.py`:

```python
import os
import sys

# Add grpc_generated/ to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "grpc_generated"))

# Setup Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yourproject.settings")
import django
django.setup()

from grpc_generated import book_pb2, book_pb2_grpc
from google.protobuf.empty_pb2 import Empty
from django_simple_grpc.client import GRPCClient

client = GRPCClient(book_pb2_grpc.BookServiceStub)
response = client.call("ListBooks", Empty())

for book in response.items:
    print(f"{book.id}: {book.title} by {book.author}")
```

---

## 🧪 Test the Full Flow

### Terminal 1 – Start the gRPC server

```bash
python manage.py run_grpc
```

---

### Terminal 2 – Run the test client

```bash
python test_client.py
```

✅ You should see a list of books from your Django database via gRPC!

---

## 📄 License

This project is open-source under the **MIT License** with an attribution clause.  
You are free to use it, but **please give credit** and **do not rebrand or publish it under your own name**.

---

## 💬 Contributions

Pull requests and feedback are welcome!  
Fork it, try it, and use it in your Django gRPC apps.

---

Made with ❤️ by HF

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

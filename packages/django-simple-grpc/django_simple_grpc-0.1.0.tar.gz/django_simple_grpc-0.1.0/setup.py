from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-simple-grpc",
    version="0.1.0",
    author="HF",
    author_email="hofattahi98@gmail.com",
    description="Simplify gRPC server and client usage in Django apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HosseinFattahi/django-simple-grpc",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=3.2",
        "grpcio==1.71.0",
        "grpcio-tools==1.71.0",
        "protobuf==5.29.4"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="django grpc grpcio microservices python server client",
    python_requires='>=3.8',
    project_urls={
        "Bug Tracker": "https://github.com/HosseinFattahi/django-simple-grpc/issues",
        "Source": "https://github.com/HosseinFattahi/django-simple-grpc",
    },
)

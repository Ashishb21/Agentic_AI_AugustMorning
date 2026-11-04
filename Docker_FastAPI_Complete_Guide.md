# Docker + FastAPI — Complete Practical Guide

## Table of Contents

1. [What is Docker?](#1-what-is-docker)
2. [Why Docker is useful for FastAPI](#2-why-docker-is-useful-for-fastapi)
3. [Containers vs Virtual Machines](#3-containers-vs-virtual-machines)
4. [Docker terminology](#4-docker-terminology)
5. [Docker images](#5-docker-images)
6. [Docker containers](#6-docker-containers)
7. [Installing and testing Docker](#7-installing-and-testing-docker)
8. [Create your first FastAPI application](#8-create-your-first-fastapi-application)
9. [requirements.txt](#9-requirementstxt)
10. [What is a Dockerfile?](#10-what-is-a-dockerfile)
11. [Dockerfile instructions](#11-dockerfile-instructions)
12. [Build a FastAPI Docker image](#12-build-a-fastapi-docker-image)
13. [Run the FastAPI container](#13-run-the-fastapi-container)
14. [Port mapping](#14-port-mapping)
15. [Container logs and shell access](#15-container-logs-and-shell-access)
16. [Environment variables](#16-environment-variables)
17. [.env files](#17-env-files)
18. [Docker networking](#18-docker-networking)
19. [Why localhost causes problems](#19-why-localhost-causes-problems)
20. [Docker Compose](#20-docker-compose)
21. [FastAPI + PostgreSQL with Compose](#21-fastapi--postgresql-with-compose)
22. [Docker volumes](#22-docker-volumes)
23. [Bind mounts and development](#23-bind-mounts-and-development)
24. [Development vs production](#24-development-vs-production)
25. [Production Dockerfile](#25-production-dockerfile)
26. [Docker image layers and caching](#26-docker-image-layers-and-caching)
27. [.dockerignore](#27-dockerignore)
28. [FastAPI project architecture](#28-fastapi-project-architecture)
29. [FastAPI + Redis](#29-fastapi--redis)
30. [Health checks](#30-health-checks)
31. [Multi-stage Docker builds](#31-multi-stage-docker-builds)
32. [Docker registries](#32-docker-registries)
33. [Image tagging](#33-image-tagging)
34. [Docker security](#34-docker-security)
35. [Docker + FastAPI production architecture](#35-docker--fastapi-production-architecture)
36. [Docker and Kubernetes](#36-docker-and-kubernetes)
37. [Essential Docker commands](#37-essential-docker-commands)
38. [Essential Docker Compose commands](#38-essential-docker-compose-commands)
39. [Complete FastAPI + Docker example](#39-complete-fastapi--docker-example)
40. [Mental model](#40-mental-model)
41. [Learning roadmap](#41-learning-roadmap)
42. [Interview questions](#42-interview-questions)
43. [Production checklist](#43-production-checklist)

---

# 1. What is Docker?

Docker is a containerization platform used to package an application and its runtime dependencies into a standardized unit called a **container**.

A container can package:

- Application source code
- Python runtime
- Python dependencies
- System libraries
- Configuration
- Startup commands

The main objective is consistency between environments.

Without Docker:

```text
Developer Machine
│
├── Python 3.12
├── FastAPI
├── Pydantic
├── PostgreSQL
└── Other dependencies
```

Another developer or production server might have different versions.

With Docker:

```text
             Docker Image
                  │
        ┌─────────┴─────────┐
        │                   │
     Container           Container
   Development           Production
        │                   │
     FastAPI              FastAPI
        │                   │
   Same dependencies   Same dependencies
```

The image becomes a reproducible package for the application.

---

# 2. Why Docker is useful for FastAPI

A FastAPI application commonly depends on:

- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy
- PostgreSQL drivers
- Redis clients
- AI/LLM SDKs
- System packages

A production AI API can have even more dependencies.

Docker makes it easier to package all of these.

Typical flow:

```text
Source Code
    │
    ↓
Dockerfile
    │
    │ docker build
    ↓
Docker Image
    │
    │ docker run
    ↓
FastAPI Container
    │
    ├── PostgreSQL
    ├── Redis
    ├── Background Workers
    └── External APIs
```

Benefits:

1. Reproducible environments
2. Easy deployment
3. Dependency isolation
4. Easy local setup
5. Consistent CI/CD
6. Easier scaling
7. Better separation between services
8. Easier rollback using image versions

---

# 3. Containers vs Virtual Machines

## Virtual Machine architecture

```text
Physical Server
│
├── Host OS
│
├── VM 1
│   ├── Guest OS
│   └── Application
│
├── VM 2
│   ├── Guest OS
│   └── Application
│
└── VM 3
    ├── Guest OS
    └── Application
```

Every VM generally contains a complete guest operating system.

## Docker architecture

```text
Physical Server
│
├── Host OS
│
└── Docker Engine
     │
     ├── Container 1
     │    └── FastAPI
     │
     ├── Container 2
     │    └── PostgreSQL
     │
     └── Container 3
          └── Redis
```

Containers share the host kernel, making them generally lighter and faster to start than full VMs.

### Important distinction

Docker is not simply a "small virtual machine."

A container is an isolated process environment that uses the host operating system's kernel.

---

# 4. Docker terminology

| Term | Meaning |
|---|---|
| Docker Engine | Software responsible for running containers |
| Docker Image | Immutable template used to create containers |
| Container | Running instance of an image |
| Dockerfile | Instructions used to build an image |
| Registry | Repository for container images |
| Docker Hub | Public container image registry |
| Volume | Persistent Docker-managed storage |
| Bind Mount | Mount a host directory/file into a container |
| Network | Allows containers to communicate |
| Docker Compose | Defines and runs multi-container applications |
| Layer | Cached filesystem/build step in an image |

The fundamental relationship is:

```text
Dockerfile
    │
    │ docker build
    ↓
Docker Image
    │
    │ docker run
    ↓
Docker Container
```

---

# 5. Docker images

A Docker image is a packaged, usually immutable template from which containers are created.

For example:

```text
fastapi-app:1.0
```

could contain:

```text
Python base image
      +
Python dependencies
      +
FastAPI
      +
Uvicorn
      +
Application code
```

One image can create many containers:

```text
             fastapi-app:1.0
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   Container 1  Container 2  Container 3
```

Images are normally composed of layers.

---

# 6. Docker containers

A container is a running or stopped instance created from an image.

Run:

```bash
docker run fastapi-app
```

List running containers:

```bash
docker ps
```

List all containers:

```bash
docker ps -a
```

Stop:

```bash
docker stop <container_id>
```

Start:

```bash
docker start <container_id>
```

Remove:

```bash
docker rm <container_id>
```

Important:

```text
Image = blueprint
Container = instance
```

An image can have multiple containers.

---

# 7. Installing and testing Docker

Install Docker Desktop on macOS or Windows, or Docker Engine on Linux.

Verify installation:

```bash
docker --version
```

Test Docker:

```bash
docker run hello-world
```

If the command completes successfully, Docker is running.

---

# 8. Create your first FastAPI application

Project:

```text
fastapi-docker/
│
├── app/
│   └── main.py
│
├── requirements.txt
└── Dockerfile
```

## app/main.py

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Hello from FastAPI + Docker"
    }


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": user_id
    }
```

Run without Docker:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# 9. requirements.txt

Create:

```text
fastapi
uvicorn[standard]
```

A more realistic API might use:

```text
fastapi
uvicorn[standard]
pydantic
sqlalchemy
psycopg2-binary
python-dotenv
redis
httpx
```

For production, pin or otherwise control dependency versions according to your project's dependency-management strategy.

---

# 10. What is a Dockerfile?

A Dockerfile describes how to construct the Docker image.

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Conceptually:

```text
Dockerfile
   │
   │ docker build
   ↓
Docker Image
```

---

# 11. Dockerfile instructions

## FROM

```dockerfile
FROM python:3.12-slim
```

Defines the base image.

The base image provides Python and the underlying userspace required to run your application.

Common choices:

```dockerfile
FROM python:3.12
```

```dockerfile
FROM python:3.12-slim
```

A slim image is often a good starting point because it reduces unnecessary packages.

---

## WORKDIR

```dockerfile
WORKDIR /app
```

Sets the working directory inside the container.

After this, commands operate relative to:

```text
/app
```

---

## COPY

```dockerfile
COPY requirements.txt .
```

Copies the requirements file from the Docker build context into `/app`.

Then:

```dockerfile
COPY ./app ./app
```

creates:

```text
/app
│
├── requirements.txt
└── app
    └── main.py
```

---

## RUN

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

Executes during **image build time**.

Important distinction:

```text
RUN
 ↓
Build time
```

versus:

```text
CMD
 ↓
Container startup
```

---

## EXPOSE

```dockerfile
EXPOSE 8000
```

Documents that the application listens on port 8000.

It does not automatically publish the port to the host.

You still need:

```bash
docker run -p 8000:8000 fastapi-app
```

---

## CMD

```dockerfile
CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]
```

This is the default command executed when the container starts.

### Why `0.0.0.0`?

If Uvicorn listens on:

```text
127.0.0.1
```

inside the container, it is bound only to the container's loopback interface.

For Dockerized web services, use:

```text
0.0.0.0
```

so the server listens on the container's network interfaces.

---

# 12. Build a FastAPI Docker image

From the project directory:

```bash
docker build -t fastapi-app .
```

Meaning:

```text
docker build
```

Build an image.

```text
-t fastapi-app
```

Assign the image name/tag.

```text
.
```

Use the current directory as the build context.

Check images:

```bash
docker images
```

---

# 13. Run the FastAPI container

Run:

```bash
docker run -p 8000:8000 fastapi-app
```

The mapping is:

```text
-p HOST_PORT:CONTAINER_PORT
```

So:

```text
localhost:8000
       │
       ↓
Container:8000
       │
       ↓
Uvicorn
       │
       ↓
FastAPI
```

Access:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Detached mode

```bash
docker run -d -p 8000:8000 fastapi-app
```

`-d` runs the container in the background.

## Give the container a name

```bash
docker run \
  --name fastapi-container \
  -p 8000:8000 \
  fastapi-app
```

---

# 14. Port mapping

Suppose FastAPI listens inside the container on port 8000.

You can expose it on host port 8080:

```bash
docker run -p 8080:8000 fastapi-app
```

Architecture:

```text
Browser
   │
   ↓
localhost:8080
   │
   ↓
Docker host port 8080
   │
   ↓
Container port 8000
   │
   ↓
FastAPI
```

The container still uses port 8000.

---

# 15. Container logs and shell access

## Logs

```bash
docker logs fastapi-container
```

Follow logs:

```bash
docker logs -f fastapi-container
```

## Open a shell

If Bash exists:

```bash
docker exec -it fastapi-container /bin/bash
```

For minimal images:

```bash
docker exec -it fastapi-container /bin/sh
```

Inside the container:

```bash
ls
```

```bash
python --version
```

```bash
pip list
```

This is very useful for debugging.

---

# 16. Environment variables

Application configuration should normally be externalized.

Avoid:

```python
DATABASE_URL = "postgresql://admin:password@localhost/mydb"
```

Prefer:

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL")
```

Run:

```bash
docker run \
  -e DATABASE_URL="postgresql://admin:password@db/mydb" \
  -p 8000:8000 \
  fastapi-app
```

Other examples:

```text
ENVIRONMENT=production
LOG_LEVEL=INFO
REDIS_URL=redis://redis:6379
MODEL_NAME=...
```

---

# 17. .env files

Example `.env`:

```env
DATABASE_URL=postgresql://postgres:password@db:5432/mydb
REDIS_URL=redis://redis:6379
ENVIRONMENT=development
```

Use:

```bash
docker run \
  --env-file .env \
  -p 8000:8000 \
  fastapi-app
```

Do not commit secrets.

Add:

```text
.env
```

to `.gitignore`.

For production, prefer a proper secret-management mechanism provided by your deployment platform rather than committing credentials to source control.

---

# 18. Docker networking

Networking becomes important when your application has multiple services:

```text
FastAPI
PostgreSQL
Redis
Worker
```

Conceptually:

```text
                 Docker Network
                       │
          ┌────────────┼────────────┐
          │            │            │
       FastAPI      PostgreSQL     Redis
       :8000          :5432        :6379
```

Containers on the same Docker network can communicate with one another.

With Compose, service names commonly act as DNS hostnames.

Example:

```text
postgresql://postgres:password@db:5432/mydb
```

Here:

```text
db
```

is the service hostname.

---

# 19. Why localhost causes problems

Suppose:

```text
fastapi-container
postgres-container
```

are separate containers.

Inside the FastAPI container:

```text
localhost
```

means:

```text
fastapi-container
```

It does not mean the PostgreSQL container.

Therefore this is normally wrong:

```text
postgresql://postgres:password@localhost:5432/mydb
```

when PostgreSQL is another container.

Use the database service name instead:

```text
postgresql://postgres:password@db:5432/mydb
```

Architecture:

```text
FastAPI container
       │
       │ db:5432
       ↓
PostgreSQL container
```

---

# 20. Docker Compose

Docker Compose is used to define and run multi-container applications.

Instead of manually running:

```bash
docker run ...
docker run ...
docker run ...
```

you define services in:

```text
compose.yaml
```

Example:

```yaml
services:

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db

  db:
    image: postgres:16
```

Start:

```bash
docker compose up
```

Background:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

---

# 21. FastAPI + PostgreSQL with Compose

Project:

```text
myproject/
│
├── app/
│   └── main.py
│
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── .env
```

Example `compose.yaml`:

```yaml
services:

  api:
    build: .
    container_name: fastapi
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:16
    container_name: postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

Architecture:

```text
                 Docker Compose
                      │
             ┌────────┴────────┐
             │                 │
          API service       DB service
             │                 │
          FastAPI          PostgreSQL
             │                 │
             └──── Docker ─────┘
                   Network
```

The API connects to:

```text
db:5432
```

not:

```text
localhost:5432
```

---

# 22. Docker volumes

Containers are designed to be replaceable.

Databases, however, need persistent storage.

Without a volume:

```text
PostgreSQL Container
        │
        ↓
Container filesystem
        │
        ↓
Container deleted
        │
        ↓
Data may be lost
```

With a volume:

```text
PostgreSQL Container
        │
        ↓
Docker Volume
        │
        ↓
Persistent data
```

Compose:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

And:

```yaml
volumes:
  postgres_data:
```

The container can be recreated while the volume remains.

---

# 23. Bind mounts and development

During development, you don't want to rebuild the image every time Python source code changes.

Use a bind mount:

```yaml
services:
  api:
    build: .
    volumes:
      - ./app:/app/app
```

Host:

```text
./app/main.py
```

is mounted into:

```text
/app/app/main.py
```

This is useful for development.

---

# 24. Development vs production

## Development

Typical characteristics:

```text
--reload
```

and source-code bind mounts:

```text
./app:/app/app
```

Example:

```yaml
command:
  - uvicorn
  - app.main:app
  - --host
  - 0.0.0.0
  - --port
  - "8000"
  - --reload
```

## Production

Usually:

- No `--reload`
- Immutable image
- Controlled configuration
- Health checks
- Structured logging
- Non-root user
- Security scanning
- Resource limits
- Proper secret management
- Multiple replicas when required

---

# 25. Production Dockerfile

Example:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]
```

### Why PYTHONDONTWRITEBYTECODE?

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
```

Prevents Python from generating `.pyc` files in the container filesystem.

### Why PYTHONUNBUFFERED?

```dockerfile
ENV PYTHONUNBUFFERED=1
```

Helps logs appear immediately rather than being buffered.

---

# 26. Docker image layers and caching

Docker images are built from layers.

Given:

```dockerfile
FROM python:3.12-slim

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
```

Conceptually:

```text
Layer 1
Python base image

Layer 2
requirements.txt

Layer 3
Installed dependencies

Layer 4
Application code
```

Docker caches layers.

This ordering is useful because application code changes frequently while dependencies change less frequently.

If you instead do:

```dockerfile
COPY . .

RUN pip install -r requirements.txt
```

then changing any source file can invalidate the layer containing dependency installation.

A common optimization is:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
```

---

# 27. .dockerignore

Create:

```text
.dockerignore
```

Example:

```text
.git
.gitignore
.env
__pycache__
*.pyc
.pytest_cache
.venv
venv
.idea
.vscode
README.md
```

Why?

The Docker build sends a build context to the Docker engine. Unnecessary files increase the context and can accidentally end up in images.

Never include secrets unnecessarily.

---

# 28. FastAPI project architecture

A real FastAPI application can be organized as:

```text
app/
│
├── main.py
│
├── api/
│   └── routes/
│       ├── users.py
│       ├── orders.py
│       └── auth.py
│
├── models/
│
├── schemas/
│
├── services/
│
├── repositories/
│
├── database/
│
├── core/
│   ├── config.py
│   └── security.py
│
└── utils/
```

Docker does not dictate your Python architecture.

Its job is to package and run the application environment.

---

# 29. FastAPI + Redis

Redis is commonly used for:

- Caching
- Rate limiting
- Sessions
- Distributed locks
- Queues
- Temporary state

Compose:

```yaml
services:

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      REDIS_URL: redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:7
```

Python:

```python
import os
from redis import Redis

redis = Redis.from_url(
    os.getenv("REDIS_URL")
)
```

The hostname is:

```text
redis
```

because it is the Compose service name.

---

# 30. Health checks

A common production problem is confusing:

```text
Container started
```

with:

```text
Application ready
```

For example, PostgreSQL's process can be running while it is not yet ready to accept connections.

Example:

```yaml
db:
  image: postgres:16

  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5
```

FastAPI should also expose a health endpoint:

```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

In larger systems, distinguish between:

- **Liveness** — process is alive
- **Readiness** — application can serve traffic

---

# 31. Multi-stage Docker builds

Multi-stage builds allow you to use one stage for building dependencies and another for the final runtime image.

Example:

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install \
    --prefix=/install \
    -r requirements.txt


FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app ./app

CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]
```

Conceptually:

```text
Builder stage
    │
    ├── Install/build dependencies
    │
    ↓
Runtime stage
    │
    ├── Required runtime dependencies
    └── Application
```

This can reduce unnecessary build tools and files in the final image.

---

# 32. Docker registries

A registry stores container images.

Examples:

- Docker Hub
- Amazon Elastic Container Registry (ECR)
- Google Artifact Registry
- Azure Container Registry
- GitHub Container Registry

Typical workflow:

```text
Developer
   │
   │ docker build
   ↓
Docker Image
   │
   │ docker push
   ↓
Container Registry
   │
   │ docker pull
   ↓
Deployment Environment
   │
   ↓
Container
```

---

# 33. Image tagging

Avoid relying only on:

```text
latest
```

Use explicit versions:

```text
fastapi-app:1.0
fastapi-app:1.1
fastapi-app:2.0
```

or immutable build identifiers:

```text
fastapi-app:a83fd21
```

Advantages:

- Traceability
- Rollbacks
- Reproducible deployments
- Easier debugging

A deployment can then identify exactly which image version is running.

---

# 34. Docker security

## Do not hard-code secrets

Avoid:

```dockerfile
ENV API_KEY=secret123
```

and:

```dockerfile
ENV DATABASE_PASSWORD=password123
```

Use environment variables or a proper secret manager.

## Run as non-root

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN chown -R appuser:appuser /app

USER appuser

CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]
```

## Other security practices

- Use trusted/minimal base images
- Keep base images updated
- Scan images for vulnerabilities
- Avoid unnecessary OS packages
- Don't run unnecessary processes as root
- Don't copy `.env` or secrets into images
- Use least-privilege permissions
- Pin/lock dependencies where appropriate
- Keep production images small

---

# 35. Docker + FastAPI production architecture

A realistic API architecture might look like:

```text
                         Internet
                            │
                            ↓
                     Load Balancer
                            │
                            ↓
                   ┌────────────────┐
                   │ Reverse Proxy  │
                   │ / Load Balancer│
                   └───────┬────────┘
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        FastAPI #1    FastAPI #2    FastAPI #3
             │             │             │
             └─────────────┼─────────────┘
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        PostgreSQL       Redis         Worker
             │             │             │
             ↓             ↓             ↓
           Data          Cache          Jobs
```

Docker can package each component.

A cloud orchestrator or platform can then manage:

- Replicas
- Health checks
- Scaling
- Networking
- Deployments
- Restarts

---

# 36. Docker and Kubernetes

Docker and Kubernetes solve different problems.

Docker:

```text
Build and run containers
```

Kubernetes:

```text
Orchestrate containers at scale
```

Conceptually:

```text
                    Kubernetes
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    FastAPI Pod     FastAPI Pod     FastAPI Pod
        │               │               │
        └───────────────┼───────────────┘
                        ↓
                  Other Services
```

A useful learning progression is:

```text
Docker
  ↓
Docker Compose
  ↓
Cloud container deployment
  ↓
Kubernetes
```

Do not start with Kubernetes before understanding containers, images, networking, volumes, and Compose.

---

# 37. Essential Docker commands

## Images

List images:

```bash
docker images
```

Pull an image:

```bash
docker pull python:3.12
```

Build:

```bash
docker build -t myapp .
```

Remove image:

```bash
docker rmi myapp
```

## Containers

List running:

```bash
docker ps
```

List all:

```bash
docker ps -a
```

Run:

```bash
docker run myapp
```

Stop:

```bash
docker stop mycontainer
```

Start:

```bash
docker start mycontainer
```

Restart:

```bash
docker restart mycontainer
```

Remove:

```bash
docker rm mycontainer
```

## Logs

```bash
docker logs mycontainer
```

Follow:

```bash
docker logs -f mycontainer
```

## Shell

```bash
docker exec -it mycontainer /bin/bash
```

or:

```bash
docker exec -it mycontainer /bin/sh
```

## Inspect

```bash
docker inspect mycontainer
```

---

# 38. Essential Docker Compose commands

Start:

```bash
docker compose up
```

Start in background:

```bash
docker compose up -d
```

Build:

```bash
docker compose build
```

Build and start:

```bash
docker compose up --build
```

Stop and remove containers/networks created by Compose:

```bash
docker compose down
```

Logs:

```bash
docker compose logs -f
```

Specific service:

```bash
docker compose logs -f api
```

Status:

```bash
docker compose ps
```

---

# 39. Complete FastAPI + Docker example

## Project structure

```text
fastapi-docker/
│
├── app/
│   └── main.py
│
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── .dockerignore
```

## app/main.py

```python
from fastapi import FastAPI

app = FastAPI(title="Docker FastAPI Demo")


@app.get("/")
async def root():
    return {
        "message": "FastAPI running inside Docker"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }
```

## requirements.txt

```text
fastapi
uvicorn[standard]
```

## Dockerfile

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]
```

## Build

```bash
docker build -t fastapi-docker .
```

## Run

```bash
docker run \
    --name fastapi-container \
    -p 8000:8000 \
    fastapi-docker
```

Open:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health endpoint:

```text
http://localhost:8000/health
```

---

# 40. Mental model

You should be able to explain the complete Docker/FastAPI lifecycle:

```text
                  Dockerfile
                      │
                      │ docker build
                      ↓
               ┌───────────────┐
               │ Docker Image  │
               └───────┬───────┘
                       │
                  docker run
                       │
                       ↓
               ┌───────────────┐
               │   Container   │
               │               │
               │    FastAPI    │
               │       │       │
               │    Uvicorn    │
               └───────┬───────┘
                       │
                  Port 8000
                       │
                       ↓
                    Client
```

For a multi-service application:

```text
                    Internet
                       │
                       ↓
                  FastAPI API
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      PostgreSQL     Redis       Worker
          │            │            │
          ↓            ↓            ↓
         Data         Cache        Jobs
```

---

# 41. Learning roadmap

## Level 1 — Docker fundamentals

Learn:

1. Images
2. Containers
3. Dockerfile
4. `docker build`
5. `docker run`
6. Ports
7. Environment variables
8. Volumes
9. Networks
10. Logs
11. `docker exec`
12. `.dockerignore`

## Level 2 — FastAPI + Docker

Learn:

13. FastAPI Dockerfile
14. Uvicorn
15. Development vs production
16. Hot reload
17. Configuration
18. Health endpoints
19. Logging
20. Error handling

## Level 3 — Multi-container applications

Learn:

21. Docker Compose
22. FastAPI + PostgreSQL
23. FastAPI + Redis
24. FastAPI + Celery/background workers
25. RabbitMQ
26. Database migrations
27. Persistent volumes
28. Docker networking

## Level 4 — Production

Learn:

29. Multi-stage builds
30. Non-root containers
31. Image optimization
32. Security scanning
33. Health checks
34. Reverse proxy
35. HTTPS
36. Load balancing
37. Horizontal scaling
38. Graceful shutdown
39. Structured logging
40. Monitoring

## Level 5 — Cloud/DevOps

Learn:

41. Container registries
42. CI/CD
43. GitHub Actions
44. AWS ECR
45. ECS/Fargate
46. Kubernetes
47. Helm
48. Kubernetes Deployments
49. Kubernetes Services
50. Horizontal Pod Autoscaling

## Level 6 — AI/LLM systems

For AI engineering, combine Docker with:

```text
                    API Gateway
                         │
                         ↓
                  FastAPI Container
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
       PostgreSQL      Redis       Background
          │              │            Worker
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                    RAG Pipeline
                         │
              ┌──────────┼──────────┐
              ↓          ↓          ↓
          Vector DB      LLM      Reranker
```

For an agentic AI application, you might additionally have:

```text
Client
  │
  ↓
FastAPI
  │
  ↓
Agent / LangGraph
  │
  ├── LLM
  ├── Vector DB
  ├── Tools
  ├── Redis
  ├── PostgreSQL
  └── Background workers
```

Docker gives you a consistent way to package these components.

---

# 42. Interview questions

## Q1. What is Docker?

Docker is a containerization platform that packages an application and its dependencies into containers so it can run consistently across environments.

## Q2. Image vs container?

An image is a packaged template. A container is a running instance of that image.

## Q3. Dockerfile vs Compose?

Dockerfile defines how an image is built.

Compose defines how multiple services/containers are configured and run together.

## Q4. Why use `0.0.0.0` with FastAPI in Docker?

Because the server must listen on the container's network interfaces so traffic forwarded from outside the container can reach it.

## Q5. Why doesn't `localhost` work for PostgreSQL in another container?

Because `localhost` inside the FastAPI container refers to the FastAPI container itself, not the PostgreSQL container.

Use the database service name:

```text
db:5432
```

## Q6. What is a Docker volume?

A persistent storage mechanism managed by Docker. It is commonly used for stateful services such as databases.

## Q7. What is Docker Compose?

A declarative way to define and run multi-container applications.

## Q8. What is a Docker layer?

Each relevant Dockerfile/build step can create a filesystem layer. Docker caches layers to speed up subsequent builds.

## Q9. Why copy requirements before application source?

To improve build caching. Application code changes frequently, while dependencies usually change less frequently.

## Q10. Should `--reload` be used in production?

Generally no. It is intended for development.

## Q11. How do you debug a container?

Useful commands:

```bash
docker ps
docker logs <container>
docker inspect <container>
docker exec -it <container> /bin/sh
```

## Q12. How do you scale a FastAPI container?

Run multiple replicas/instances behind a load balancer or use a container orchestrator such as Kubernetes or a cloud container service.

---

# 43. Production checklist

Before deploying a Dockerized FastAPI application, check:

## Application

- [ ] FastAPI application starts correctly
- [ ] Uvicorn/Gunicorn strategy is appropriate for your deployment
- [ ] `/health` or readiness endpoint exists
- [ ] Configuration is externalized
- [ ] Secrets are not hard-coded
- [ ] Logging is configured
- [ ] Graceful shutdown is considered

## Dockerfile

- [ ] Appropriate base image
- [ ] Dependencies installed efficiently
- [ ] `.dockerignore` exists
- [ ] Image is reasonably small
- [ ] Application does not unnecessarily run as root
- [ ] No secrets baked into the image
- [ ] Build caching is effective

## Runtime

- [ ] Correct port mapping
- [ ] Correct environment variables
- [ ] Health checks
- [ ] Resource limits where appropriate
- [ ] Restart strategy
- [ ] Persistent volumes for required state

## Database

- [ ] PostgreSQL is externalized or managed appropriately
- [ ] Database credentials are secured
- [ ] Database migrations are handled
- [ ] Backups exist
- [ ] Connection pooling is configured appropriately

## Deployment

- [ ] Image is pushed to a registry
- [ ] Images have traceable tags
- [ ] CI/CD builds and tests the image
- [ ] Vulnerability scanning is performed
- [ ] Rollback strategy exists
- [ ] Monitoring and alerting exist

---

# Final summary

The most important Docker + FastAPI concepts can be reduced to this:

```text
Dockerfile
    │
    │ docker build
    ↓
Docker Image
    │
    │ docker run
    ↓
FastAPI Container
    │
    ├── Port mapping
    ├── Environment variables
    ├── Docker network
    └── Volumes
            │
            ├── PostgreSQL
            └── Redis
```

And for production:

```text
                    Internet
                       │
                       ↓
                 Load Balancer
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
      FastAPI #1   FastAPI #2   FastAPI #3
          │            │            │
          └────────────┼────────────┘
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        PostgreSQL             Redis
             │                   │
             ↓                   ↓
            Data                Cache
```

The key mental model is:

**Dockerfile → Image → Container → Network/Ports → Services → Production deployment.**

For FastAPI specifically, master:

```text
Dockerfile
    +
Uvicorn
    +
Port mapping
    +
Environment variables
    +
Docker Compose
    +
PostgreSQL
    +
Redis
    +
Health checks
    +
Production security
```

These concepts form the foundation for deploying production FastAPI, RAG, and agentic AI applications in containers.

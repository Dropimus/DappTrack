# DappTrack Backend (Dockerized)

This repository contains the **Dockerized backend** for the DappTrack app, including:
- FastAPI server
- PostgreSQL database
- Redis queue
- Celery worker and beat scheduler
- Docker Secrets for secure config

---

## 🚀 Getting Started (with Docker)

> **Requirements**
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

### 1. Clone the Repo

```bash
git clone https://github.com/DappTrack/DappTrack.git
cd DappTrack/server
````

### 2. Add Docker Secrets

Create a `secrets/` directory with the following files inside `DappTrack/server/secrets/`:

```
db_url
redis_url
secret_key
postgres_user
postgres_password
postgres_db
postgres_host
postgres_port
celery_broker_url
celery_result_backend
```

Each file should contain a single value (no extra whitespace or line breaks). For example:

**`postgres_user`**

```
my_db_user
```

**`postgres_password`**

```
my_db_password
```

Adjust file names and contents to match the names used in `docker-compose.yml`.

### 3. Build & Start All Services

```bash
docker compose up --build
```

This will start:

* FastAPI app at `http://localhost:8000`
* PostgreSQL database
* Redis queue
* Celery worker
* Celery beat scheduler

### 4. API Documentation

Once running, visit:

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🐳 Docker Commands

* Stop containers:

  ```bash
  docker compose down
  ```

* Rebuild and recreate containers:

  ```bash
  docker compose up --build --force-recreate
  ```

* View logs:

  ```bash
  docker compose logs -f
  ```

---

## 📱 For Mobile Developers

To integrate the mobile app with this backend:

1. Clone the repo and navigate to `DappTrack/server`.
2. Run:

   ```bash
   docker compose up
   ```
3. Access the API at `http://localhost:8000` (or `http://host.docker.internal:8000` for emulators).

---

## 🤝 Contributing

1. Fork this repository.
2. Create a branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes and push to your fork.
4. Open a pull request on GitHub.

---

## 📄 License

MIT License — © 2025 Victor Uko & DappTrack Team

```

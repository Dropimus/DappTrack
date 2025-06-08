# DappTrack

DappTrack is a Web3 Airdrop tracking application backend built with FastAPI, PostgreSQL, Redis, and served behind an Nginx API gateway. The project is containerized with Docker Compose for easy setup and deployment.

---

## Features

- FastAPI backend for handling API requests
- PostgreSQL as the main database
- Redis for caching and Celery task queue
- Nginx reverse proxy to route requests and handle API gateway responsibilities
- Dockerized environment for consistent deployment and local development

---

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

---

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/DappTrack/DappTrack.git
cd DappTrack
````


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

3. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

4. Access the FastAPI documentation at:

   ```
   http://localhost/api/docs
   ```

---

## Docker Compose Services

* **server**: FastAPI backend server, running on port `8000`
* **db**: PostgreSQL database, exposed on port `5433`
* **redis**: Redis instance for caching and Celery, exposed on port `6379`
* **api\_gateway**: Nginx reverse proxy routing requests to the backend API

---

## Configuration

* Nginx is configured to proxy requests from `/api/` to the FastAPI server.
* Environment variables for database credentials, Redis, and others should be set in `./server/secrets`.

---

## Common Commands

* Start containers in detached mode:

  ```bash
  docker-compose up -d
  ```

* Stop containers:

  ```bash
  docker-compose down
  ```

* View logs for a service:

  ```bash
  docker-compose logs -f <service_name>
  ```

* Remove orphan containers:

  ```bash
  docker-compose up --remove-orphans
  ```

---

## Troubleshooting

* **Port conflicts**: If you get errors about ports already in use, ensure no other containers or services are occupying those ports or adjust the ports in `docker-compose.yml`.
* **Nginx upstream host not found**: Make sure the service name in your `nginx.conf` matches the Docker Compose service name for the FastAPI backend.
* **Missing files in volume mounts**: Verify host paths used in volume mounts exist and are the correct type (file vs directory).

---

## License

MIT License

---

## Contact

Created by Victor Uko
Email: [ukovictor8@gmail.com](mailto:ukovictor8@gmail.com)
GitHub: [https://github.com/victork19](https://github.com/victork19)

```
```

Sure — here’s a clean, copy-paste ready `README.md` for the `server/` directory in your updated project structure:

# DappTrack Server

This is the **FastAPI** backend service of the DappTrack platform. It exposes API endpoints for the mobile app and other services to interact with the core system.

---

## 🔧 Features

- FastAPI-powered backend
- RESTful endpoints
- Handles requests from mobile and internal services
- Runs behind NGINX reverse proxy
- Uses Docker and environment-based secrets

---


---

## 🚀 Running the Server

The server runs as part of the entire DappTrack system using **Docker Compose** from the root of the project.

From the project root:

```bash
docker-compose up --build
````

The FastAPI server will be accessible at:

```
http://localhost/api
```

To access API docs:

```
http://localhost/api/docs
```

---

## 🔐 Environment Variables

Secrets and configurations are injected via **Docker secrets**. No `.env` is used in production.


---

## 📦 Dependencies

* FastAPI
* Uvicorn
* Python 3.10+
* Docker

Install locally for development:

```bash
cd server
pip install -r requirements.txt
```

---

## 📱 Mobile App Integration

The mobile app interacts with this service via the `/api` routes exposed through NGINX.

Make sure the mobile team uses the correct base URL and understands any required headers/auth methods.

---

## 🛠 Dev Notes

* Internal services (e.g., inference, ingestion) interact with this via internal networking in Docker.
* Logging, monitoring, and error tracking should be configured as the system matures.



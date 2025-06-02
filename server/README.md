# DappTrack Backend (Dockerized)

This repository contains the **Dockerized backend** for the DappTrack app, including:
- FastAPI server
- PostgreSQL database
- Redis queue
- Celery worker and beat scheduler
- Docker Secrets for secure config

---

## Getting Started (with Docker)

> **Requirements**
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/)

### 1. Clone the Repo

```bash
git clone https://github.com/DappTrack/DappTrack.git
cd DappTrack/server

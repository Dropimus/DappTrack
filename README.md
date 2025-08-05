# **Dropimus**

*The Trust Layer for Web3 Airdrops*


---

## **Overview**

Dropimus is building the infrastructure to restore trust in the **\$10B+ Web3 airdrop economy**. Over **\$2B was lost to scam airdrops in 2024**, and the problem is growing. Dropimus provides:

* **Multi-chain airdrop tracking** (EVM, Solana, and more)
* **AI-driven fraud detection** (Proof of Integrity)
* **Proof of Person** for Sybil resistance
* **Airdrop Derivative Market (ADM)** for trading speculative positions on upcoming airdrops

---

## **Vision**

To make airdrops transparent, secure, and financialized, creating an ecosystem where **incentives drive growth—not scams**.

---

## **Architecture**

* **Backend:** FastAPI (Python)
* **Frontend:** React Native (UI in progress), Flet MVP for demo
* **AI Layer:** Placeholder structure for fraud detection models
* **Scripts:** Data scrapers for airdrop aggregation
* **Smart Contracts:** Proof of Integrity & ADM logic (future on-chain implementation)
* **Containerization:** Docker for services

```
DappTrack/
├── storage/            # Persistent storage for models and data
├── feedback/           # Feedback loop for AI improvements
├── preprocessing/      # Preprocessing scripts for AI pipelines
├── inference/          # Model inference service
├── server/             # FastAPI backend API
├── ai/                 # Placeholder for AI modules (under development)
├── ingestion/          # Ingestion layer for airdrop data sources
├── trainer_service/    # Model training service
└── docker-compose.yml

```

> **Note:** The project began as **DappTrack**, and some directories retain that name. All branding now reflects **Dropimus**, with full migration planned in future updates.

---

## **Tech Stack**

* **Backend:** FastAPI, Python
* **Mobile App:** React Native (separate repo), Flet MVP for demo
* **AI:** TensorFlow / PyTorch (planned)
* **Blockchain:** EVM-compatible + Solana integration
* **Containerization:** Docker

---

## **Installation**

```bash
# Clone the repo
git clone https://github.com/dropimus/dapptrack.git
cd DappTrack/server

# Install dependencies
pip install -r requirements.txt

# Run with Docker
docker-compose up --build
```

---

## **Roadmap**

✅ MVP: Multi-chain airdrop tracking
✅ AI-driven scam detection (Proof of Integrity - in progress)
[] Proof of Person (voice verification + future ZK)
[] ADM (Airdrop Derivative Market)
[] Full decentralization

---

## **Contact**

**Email:** [contact@dropimus.com ](mailto:contact@dropimus.com )
**GitHub:** [https://github.com/victork19](https://github.com/victork19)

---

## **License**

**All Rights Reserved**
This repository contains the Dropimus backend MVP and placeholder AI structure for demonstration purposes.
Advanced components (AI models, smart contracts) remain under private development and are excluded to protect intellectual property.

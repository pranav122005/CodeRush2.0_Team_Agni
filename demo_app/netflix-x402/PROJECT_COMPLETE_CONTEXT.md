# 🚀 Project Context: Netflix x402 & NEXUS Settlement Mesh

## 📌 Executive Summary
This project implements an **enterprise-grade, non-custodial HTTP 402 Payment & Verification Middleware System** called **NEXUS Mesh**, integrated directly into a **Netflix-inspired Resource Server** web application. 

The system enables seamless, decentralized pay-per-view access to digital resources across multi-chain ecosystems (Algorand, Ethereum/EVM, Solana/SVM) by standardizing payment payloads, preventing double-spending/replays, maintaining non-custodial transaction state, and automatically failing over across facilitators when primary public endpoints degrade or fail.

---

## 🏗️ Architecture Overview

The system consists of three main decoupled services operating together:

```
+-----------------------------------------------------------------------------------+
|                                  USER / CLIENT                                    |
|                           (Browser / Agent Platform)                              |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | HTTP Requests
                                          v
+-----------------------------------------------------------------------------------+
| 🎬 FRONTEND: Netflix x402 Web Application (Vite + React)                          |
|    - Port: 5173                                                                   |
|    - Triggers x402 Challenge workflows & dynamic payment modal                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | REST API (HTTP 402 / JSON)
                                          v
+-----------------------------------------------------------------------------------+
| ⚙️ BACKEND: Netflix Resource Server (FastAPI + SQLite)                            |
|    - Port: 8000                                                                   |
|    - Protects video content routes, offloads verification/settlement to Mesh      |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Internal REST API
                                          v
+-----------------------------------------------------------------------------------+
| 🔗 MIDDLEWARE: NEXUS Verification & Settlement Mesh (FastAPI)                     |
|    - Port: 8001                                                                   |
|    - Replay Guard (SHA-256 Hash Ring)                                             |
|    - Settlement State Machine                                                     |
|    - Facilitator Engine & Circuit Breakers                                        |
|    - Multi-Chain Adapters (Algorand GoPlausible, Algorand/EVM/SVM Simulators)     |
|    - HMAC-SHA256 Receipt Service                                                  |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ System Components & Directory Breakdown

```
netflix-x402/
├── start.ps1                       # One-click startup script for all 3 services
├── PROJECT_COMPLETE_CONTEXT.md     # Full project documentation & architectural reference
│
├── frontend/                       # React Web Application (Port 5173)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Header with wallet status
│   │   │   ├── MovieGrid.jsx       # Catalog of paywall-protected movies
│   │   │   ├── PaymentModal.jsx    # x402 Multi-chain payment interface
│   │   │   └── VideoPlayer.jsx     # Streaming player unlocked via valid receipt
│   │   ├── services/
│   │   │   └── api.js              # Axios HTTP client connecting to Backend (Port 8000)
│   │   └── App.jsx
│
├── backend/                        # Netflix Resource Server (Port 8000)
│   ├── main.py                     # FastAPI application entrypoint & HTTP 402 challenge handler
│   ├── models.py                   # SQLAlchemy models (PaymentRecord, Receipt)
│   ├── schemas.py                  # Pydantic data schemas
│   ├── database.py                # SQLite database configuration
│   └── services/
│       ├── payment.py              # Connects Backend to NEXUS Mesh via HTTP
│       └── receipt.py              # Local PDF receipt generator
│
└── nexus-mesh/                     # Verification & Settlement Engine (Port 8001)
    ├── app/
    │   ├── main.py                 # Mesh application entrypoint & facilitator bootstrap
    │   ├── config.py               # Mesh settings & environment variables
    │   ├── api/
    │   │   └── router.py           # REST endpoints (/verify, /settle, /receipt, /health)
    │   ├── compatibility/
    │   │   └── parser.py           # x402 v2 payment header & requirement parser
    │   ├── verification/
    │   │   └── replay_guard.py     # In-memory SHA-256 idempotency & duplicate detector
    │   ├── registry/
    │   │   ├── base.py             # Abstract BaseFacilitator interface
    │   │   ├── circuit_breaker.py  # Closed/Open/Half-Open state monitor
    │   │   └── engine.py           # FacilitatorEngine routing & failover executor
    │   ├── settlement/
    │   │   ├── state_machine.py    # Transaction lifecycle tracker (PENDING -> VERIFIED -> SETTLING -> SETTLED)
    │   │   └── adapters/           # Blockchain network settlement adapters
    │   │       ├── algorand.py     # GoPlausible Live Facilitator + Local Algorand Simulator
    │   │       ├── ethereum.py     # EVM Sepolia Simulator Adapter
    │   │       └── solana.py       # SVM Devnet Simulator Adapter
    │   └── receipt/
    │       └── generator.py        # HMAC-SHA256 cryptographic receipt signer
```

---

## ⚡ NEXUS Mesh Core Concepts

### 1. Facilitator Engine & Circuit Breaker Pattern
The `FacilitatorEngine` maintains a pool of network adapters. Every live external facilitator node is monitored by an isolated `CircuitBreaker`:

- **State `CLOSED` (Normal):** Requests route directly to the primary live facilitator (e.g., `AlgorandGoPlausibleFacilitator`).
- **State `OPEN` (Tripped):** After 3 consecutive failures or timeouts, the circuit trips `OPEN` for 30 seconds.
- **Automatic Fallback:** While primary is `OPEN`, the engine seamlessly redirects settlement traffic to registered **Simulator Adapters** (or backup live nodes) with zero downtime to the Resource Server.

### 2. Idempotency & Replay Guard
- Every incoming `Payment-Signature` payload is hashed using SHA-256 (`payload_hash`).
- If a client attempts to submit the same signed payload twice, the `ReplayGuard` blocks execution immediately with a `409 Conflict` error, returning the original `trace_id`.

### 3. Settlement State Machine
Every payment transaction progresses through explicit states:
1. `PENDING`: Payment trace created.
2. `VERIFIED`: Payload validated against payment requirements.
3. `SETTLING`: Submitted to chosen network facilitator.
4. `SETTLED`: Confirmed on-chain or simulated; cryptographic receipt generated.
5. `FAILED`: Terminal state if all nodes fail.

### 4. Receipt Engine
Upon settlement, NEXUS Mesh issues a verifiable receipt containing:
- `receipt_id`: Unique identifier (`rcpt_...`).
- `trace_id`: Mesh settlement trace reference.
- `signature`: HMAC-SHA256 signature generated using a secret key.

---

## 🔄 End-to-End Payment Protocol Flow

1. **Content Request:** Client requests `/api/v1/content/movie1` on Port 8000.
2. **402 Challenge:** Backend responds with `HTTP 402 Payment Required` with pricing & network metadata.
3. **Payload Submission:** Frontend opens modal, formats signed payload, and posts to Backend `/api/v1/payments/verify`.
4. **Verification Step:** Backend forwards request to NEXUS Mesh `/api/v1/verify` (Port 8001). Replay guard validates hash and issues `trace_id`.
5. **Settlement Step:** Backend calls NEXUS Mesh `/api/v1/settle`. Mesh selects healthy facilitator, executes on-chain/simulated settlement, and signs HMAC receipt.
6. **Access Granted:** Backend marks transaction as `succeeded` in SQLite, generates PDF receipt, and grants video stream access URL to frontend.

---

## 🚀 How to Run the Project

### One-Click Launch (Recommended)
Open PowerShell in the `netflix-x402` folder and run:
```powershell
.\start.ps1
```
This automatically launches all three required servers in separate windows.

### Manual Launch (3 Terminals)

1. **NEXUS Mesh (Port 8001):**
   ```powershell
   cd netflix-x402\nexus-mesh
   ..\backend\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Netflix Backend (Port 8000):**
   ```powershell
   cd netflix-x402\backend
   .\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Netflix Frontend (Port 5173):**
   ```powershell
   cd netflix-x402\frontend
   npm run dev
   ```

---

## 🌐 Endpoints Reference

### ⚙️ Backend (Port 8000)
- `GET /api/v1/content/{content_id}` – Fetch protected video link (Returns 402 if unpurchased).
- `POST /api/v1/payments/verify` – Process payment signature via NEXUS Mesh.
- `GET /api/v1/receipts/{receipt_id}` – Download local PDF receipt.

### 🔗 NEXUS Mesh (Port 8001)
- `POST /api/v1/verify` – Validate x402 header & check replay guard.
- `POST /api/v1/settle` – Route settlement through Facilitator Engine.
- `GET /api/v1/health` – Returns live status of mesh & circuit breakers.
- `GET /api/v1/facilitators` – Lists all registered multi-chain facilitators.

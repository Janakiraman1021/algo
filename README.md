# AgentPay — A2A + x402 + Algorand AI Agent Marketplace

> **Autonomous Agent-to-Agent (A2A) Marketplace settling AI task micropayments via the x402 HTTP standard on Algorand TestNet.**

---

## 1. What is AgentPay?

**AgentPay** is a decentralized, machine-to-machine AI agent marketplace where autonomous AI agents can discover, request, and pay for services from other AI agents in real time.

In traditional Web2 architectures, AI agents cannot autonomously pay for API resources without human credit card friction. AgentPay solves this by combining:
1. **Agent-to-Agent (A2A) Messaging Protocol**: Lightweight JSON-RPC style communication between Buyer and Seller agents.
2. **x402 Micropayments**: Native HTTP 402 Payment Required challenges and cryptographic settlement proofs.
3. **Algorand Blockchain**: Sub-3-second transaction finality, sub-cent fees, and high throughput for instant machine micropayments.
4. **AgentPayRegistry Smart Contract**: On-chain usage ledger recording verified tasks, agent identity, service pricing, and aggregate payment volume.

---

## 2. System Architecture & Flow

```
+-----------------------------------------------------------------------------------------+
|                                Next.js 14 Web3 Frontend                                 |
|  - Dark futuristic glassmorphism dashboard (Tailwind CSS, Lucide icons)                 |
|  - Real-time step progress visualizer & interactive task submission                     |
+--------------------------------------------+--------------------------------------------+
                                             | (POST /api/tasks)
                                             v
+-----------------------------------------------------------------------------------------+
|                                   FastAPI Main Backend                                  |
|                                                                                         |
|   +-----------------------+                         +-------------------------------+   |
|   |      Buyer Agent      |                         |     Seller (Summary Agent)    |   |
|   |     (BuyerAgent)      |                         |        (SummaryAgent)         |   |
|   +-----------+-----------+                         +---------------+---------------+   |
|               |                                                     ^                   |
|               |  (1) A2A Task Request (Unpaid)                      |                   |
|               +---------------------------------------------------->+                   |
|               |                                                     |                   |
|               |  (2) HTTP 402 Payment Required (x402 Challenge)     |                   |
|               +<----------------------------------------------------+                   |
|               |                                                     |                   |
|               |  (3) Signs & Broadcasts Tx on Algorand TestNet      |                   |
|               |      (Transfers 0.01 USDC to Seller Address)        |                   |
|               |                                                     |                   |
|               |  (4) Retries A2A Request with Tx Payment Proof      |                   |
|               +---------------------------------------------------->+                   |
|               |                                                     |                   |
|               |                                     (5) Verifies Payment on-chain       |
|               |                                     (6) Executes AI Summarizer          |
|               |                                     (7) Records Task in Smart Contract  |
|               |                                                     |                   |
|               |  (8) Returns AI Summary + TxID + AppID Metadata    |                   |
|               +<----------------------------------------------------+                   |
|               |                                                                         |
|   +-----------v---------------------------------------------------------------------+   |
|   | AI Engine Abstraction: Gemini-1.5-Flash / Groq LLaMA-3.3 / OpenAI / Fallback    |   |
|   +---------------------------------------------------------------------------------+   |
+--------------------------------------------+--------------------------------------------+
                                             |
                         +-------------------+-------------------+
                         |                                       |
                         v                                       v
+------------------------------------+       +--------------------------------------------+
|        x402 Payment Adapter        |       |              Algorand TestNet              |
|  - Official x402 AVM adapter (TS)  |       |  - Real USDC / ALGO transfer settlement   |
|  - Challenge generation & format   |       |  - AgentPayRegistry Smart Contract (Puya)  |
|  - Node-based facilitator client   |       |  - Lora Explorer: lora.algokit.io          |
+------------------------------------+       +--------------------------------------------+
```

---

## 3. Why A2A? Why x402? Why Algorand? Why Smart Contracts?

| Component | Why It Matters |
| :--- | :--- |
| **A2A Protocol** | Standardizes agent discovery, capabilities declaration, task dispatching, and response structures across heterogeneous agent frameworks. |
| **x402 Micropayments** | Native HTTP protocol standard that turns status code `402 Payment Required` into an automated payment handshake for machine-to-machine APIs. |
| **Algorand Blockchain** | Instant block finality (~3.3s) and micro-fees (~0.001 ALGO / ~$0.0002) make true sub-cent micropayments economically feasible. |
| **Smart Contract Registry** | Provides decentralized auditability, non-custodial usage proofs, verifiable agent track records, and transparent marketplace volume. |

---

## 4. Technology Stack

- **Frontend**: Next.js 14 (App Router), React 18, Tailwind CSS, Lucide React, Glassmorphism UI.
- **Main Backend**: Python 3.12+, FastAPI, Pydantic v2, `py-algorand-sdk`, `httpx`, `python-dotenv`, `pytest`.
- **AI Engine**: Google Gemini REST API / Groq LLaMA-3.3 / OpenAI / Local deterministic fallback.
- **x402 Adapter**: Node.js, TypeScript, Express, Algorand SDK.
- **Smart Contract**: Algorand Python (PuyaPy / ARC-4 / ARC-56) compiled to TEAL v8 bytecode.

---

## 5. Project Structure

```
agentpay/
├── frontend/                     # Next.js 14 Web3 Dashboard
│   ├── app/
│   │   ├── globals.css           # Custom glassmorphic styling & neon accents
│   │   ├── layout.tsx            # App root layout
│   │   └── page.tsx              # Interactive marketplace & live execution visualizer
│   ├── lib/
│   │   └── api.ts                # Backend API client
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── backend/                      # FastAPI Main Backend
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint with CORS & lifecycle
│   │   ├── config.py             # Pydantic environment configuration
│   │   ├── routes/               # REST API route handlers
│   │   ├── agents/               # BuyerAgent & SummaryAgent logic
│   │   ├── blockchain/           # Algorand TestNet client & contract caller
│   │   ├── ai/                   # Multi-provider LLM summarizer
│   │   └── models/               # Pydantic schemas & A2A types
│   ├── tests/                    # Backend API unit & integration tests
│   ├── requirements.txt
│   └── .env.example
│
├── x402-adapter/                 # TypeScript x402 Payment Facilitator
│   ├── src/
│   │   └── index.ts              # x402 challenge & settlement server (Port 4020)
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── smart-contract/               # Algorand Smart Contract
│   ├── contracts/
│   │   ├── agent_pay_registry.py # PuyaPy / Algorand Python contract
│   │   └── teal_generator.py     # ARC-4 & ARC-56 TEAL generator
│   └── tests/
│       └── test_agent_pay_registry.py
│
├── scripts/                      # Setup & Deployment Utilities
│   ├── setup_testnet.py          # Generates Buyer & Seller TestNet accounts
│   ├── deploy_contract.py        # Compiles & deploys AgentPayRegistry to TestNet
│   └── seed_agent.py             # Registers agent & service on-chain
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 6. Quick Start & Local Development

### Step 1: Clone and Set Up Wallets

Generate your TestNet Buyer and Seller keypairs:
```bash
python scripts/setup_testnet.py
```
This will print two Algorand TestNet addresses (Buyer & Seller) and create `backend/.env`.

Fund both addresses with free TestNet ALGO:
- 👉 [Algorand TestNet Dispenser](https://bank.testnet.algorand.network/)

---

### Step 2: Deploy the Smart Contract (Optional / Automated)

Deploy the `AgentPayRegistry` smart contract to Algorand TestNet:
```bash
python scripts/deploy_contract.py
```
This outputs your new `App ID` and updates your environment configuration.

Seed the agent into the registry:
```bash
python scripts/seed_agent.py
```

---

### Step 3: Run Backend, Adapter, and Frontend

#### Terminal 1: FastAPI Main Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

#### Terminal 2: x402 TypeScript Adapter
```bash
cd x402-adapter
npm install
npm run dev
```
- Service URL: http://localhost:4020/health

#### Terminal 3: Next.js Web3 Frontend
```bash
cd frontend
npm install
npm run dev
```
- Dashboard: http://localhost:3000

---

## 7. End-to-End Demo Workflow

1. Open **http://localhost:3000** in your browser.
2. View **Summary Agent** ($0.01 USDC / request) in the marketplace.
3. Select one of the quick test prompts or write custom text.
4. Click **"Ask Agent & Settle 0.01 USDC on Algorand"**.
5. Observe the live 7-step visual transaction pipeline:
   - **Step 1**: User task intake.
   - **Step 2**: BuyerAgent dispatches A2A message.
   - **Step 3**: SummaryAgent returns HTTP 402 challenge.
   - **Step 4**: BuyerAgent signs payment on Algorand TestNet.
   - **Step 5**: Transaction confirms on-chain.
   - **Step 6**: SummaryAgent executes AI summarization.
   - **Step 7**: `AgentPayRegistry` updates on-chain metrics.
6. Click **"View on Algorand Explorer"** to inspect the real transaction on AlgoKit Lora Explorer!

---

## 8. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Node connection, App ID, and system health |
| `GET` | `/api/agents` | List all available AI agents |
| `GET` | `/api/services` | List priced AI services |
| `POST` | `/api/tasks` | Execute end-to-end A2A + x402 task |
| `POST` | `/api/a2a/summary` | Direct A2A protocol endpoint (with 402 challenge) |
| `GET` | `/api/transactions/{tx_id}` | Verify on-chain transaction status |
| `GET` | `/api/stats` | Aggregate marketplace stats & volume |

---

## 9. Running Tests

Run all unit and integration tests across smart contracts and backend:
```bash
python -m pytest smart-contract/tests backend/tests -v
```

---

## 10. Security & Hackathon Best Practices

- **Zero Client-Side Secrets**: Private keys and mnemonics are stored exclusively on the secure backend and never exposed to the frontend browser.
- **On-Chain Cryptographic Verification**: Payments are verified directly via Algorand TestNet Algod nodes before executing LLM workloads.
- **Graceful Fallbacks**: The AI engine supports multi-provider fallback (Gemini ➔ Groq ➔ OpenAI ➔ Local Engine) ensuring zero downtime during hackathon presentations.

# 🛡️ ShieldAgent: Autonomous PayPal Dispute Defense Platform
> **Built for the PayPal AI Hackathon: Build what’s next with PayPal and AI**  
> *Targeting: **Best Use of Agentic Commerce ($5,000)** & **Best Use of PayPal + AI ($5,000)***

ShieldAgent is an autonomous agentic commerce defense system engineered for PayPal merchants. It intercepts inbound card chargebacks and disputes, executes multimodal forensic audits, enforces card network rules (**Visa Compelling Evidence 3.0** & **Mastercard Scheme Standards**), and autonomously synthesizes and submits winning representment packages directly to the **PayPal Disputes REST API**.

---

## 🎯 The Core Problem: The $100 Billion Friendly Fraud Drain

* **70%+ of Chargebacks are Friendly Fraud:** Cardholders make legitimate purchases and subsequently claim *"I didn't authorize this"* or *"Package never arrived"*.
* **Staggered, Strict Deadlines:** Card schemes enforce strict 7–10 day representment windows. Merchants managing claims by hand often miss deadlines, resulting in default losses.
* **Complex Network Rules:** Card schemes update rules constantly (e.g. Visa CE 3.0, Mastercard mandatory prior merchant contact). Small merchants rarely know how to leverage these rules to automatically force liability shifts back to the issuing bank.
* **The $500 Arbitration Trap:** Escalating an unwinnable dispute to Stage 9 Scheme Arbitration carries non-refundable **$500+ filing fees for the loser**, causing severe financial damage to merchants.

---

## 💡 How ShieldAgent Solves It

ShieldAgent acts as an autonomous financial defense council with 4 specialized AI agents:

```
[ PayPal Dispute Webhook ] 
           │
           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Multi-Agent Defense Council                       │
│                                                                        │
│  1. Triage Agent: Calculates Win Prob, Day N-1 SLA & $500 Arb EV       │
│  2. Forensic Auditor: Carrier POD GPS matching & photo EXIF audit      │
│  3. Compliance Agent: Enforces Visa CE 3.0 & Mastercard scheme rules   │
│  4. Representment Agent: Compiles formal dossiers & PayPal payloads    │
└────────────────────────────────────────────────────────────────────────┘
           │
           ▼
[ Autonomous Action Engine ]
• Winnable (>90%): Submits evidence dossier to PayPal Disputes REST API
• Negative EV / High Risk: Concedes early to save $20 dispute fee or $500 penalty
```

---

## 🌟 Key Capabilities

### 1. 10-Stage Scheme Lifecycle Management (Barclays / Visa / Mastercard)
* Normalizes disputes across Visa VROL and Mastercard Mastercom scheme standards.
* **Mastercard Procedural Checks:** Automatically refutes disputes where the cardholder failed to attempt prior merchant resolution.
* **Stage 9 Arbitration Radar:** Evaluates mathematical Expected Value (EV) against the \$500 network filing fee, preventing catastrophic fee penalties on shaky claims.

### 2. Visa Compelling Evidence 3.0 (CE 3.0) Engine
* Scans merchant database for $\ge 2$ prior settled, undisputed transactions (120–365 days old) sharing matching IP or postal code.
* **Guarantees automated liability shift** back to the issuing bank pursuant to Visa Core Rules.

### 3. Multimodal Forensic Evidence Lab
* Accepts real delivery receipts, drop-off photos, and customer damage claims.
* Extracts camera hardware, timestamp, and GPS coordinates from EXIF metadata to flag fabricated evidence.

### 4. Printable Representment Packets
* Generates formal, underwriter-ready dispute packets viewable at `/api/v1/disputes/{id}/dossier/html`, formatted for card scheme review.

---

## 🚀 One-Click Quickstart Guide

You can run both the backend and frontend with a single command:

```bash
# Clone the repository
git clone https://github.com/omganjewar-devv/PayPal-ShieldAgent.git
cd PayPal-ShieldAgent

# Launch both Backend & Frontend with zero configuration
./run.sh
```

Once started:
* **Merchant Command Center:** [http://localhost:3000](http://localhost:3000)
* **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Sample Printable Representment Packet:** [http://localhost:8000/api/v1/disputes/PP-D-83921/dossier/html](http://localhost:8000/api/v1/disputes/PP-D-83921/dossier/html)

---

## 🧪 Interactive Simulation Testbench

ShieldAgent includes pre-configured test scenarios ready to test from the UI or API:

| Scenario | Scheme Rail | Agent Action | Win Probability |
| :--- | :--- | :--- | :--- |
| **1. Friendly Fraud (INR)** | Visa (Reason 13.1) | **DEFEND** (Carrier POD Verified) | **92%** |
| **2. Visa CE 3.0 Match** | Visa (Reason 10.4) | **DEFEND** (Liability Shifted to Issuer) | **98%** |
| **3. Mastercard Prior Contact Defect** | Mastercard (Reason 4853) | **DEFEND** (Procedural Scheme Defect) | **96%** |
| **4. Scheme Arbitration Risk ($500)** | Visa (Reason 13.3) | **CONCEDE_ARBITRATION** (Avoids $500 Fee) | Negative EV Deflected |

---

## ☁️ Cloud Deployment (Render Blueprint)

ShieldAgent is cloud-ready with a native `render.yaml` blueprint:
1. Connect your repository on [Render](https://render.com).
2. Render automatically discovers `render.yaml` and deploys both the FastAPI Backend and Vite static frontend.

---

## 📜 PayPal Developer Platform API Integration

| PayPal Endpoint | HTTP Method | Usage in ShieldAgent |
| :--- | :--- | :--- |
| `/v1/customer/disputes` | `GET` | Fetches active dispute queue |
| `/v1/customer/disputes/{id}` | `GET` | Retrieves reason codes and disputed transactions |
| `/v1/customer/disputes/{id}/provide-evidence` | `POST` | Autonomously submits representment dossiers |
| `/v1/customer/disputes/{id}/accept-claim` | `POST` | Autonomously resolves negative EV disputes |
| `/v1/notifications/webhooks` | `POST` | Ingests `CUSTOMER.DISPUTE.CREATED` events |

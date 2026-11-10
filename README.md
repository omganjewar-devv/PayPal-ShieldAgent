# 🛡️ ShieldAgent: Autonomous Dispute Defense & Representment Engine
> **Built for the PayPal AI Hackathon: Build what’s next with PayPal and AI**

ShieldAgent is an autonomous agentic defense system engineered for PayPal merchants. It intercepts incoming card chargebacks and disputes, runs multimodal forensic audits, leverages complex card network rules (such as **Visa Compelling Evidence 3.0**), and autonomously synthesizes and submits winning representment packages directly through the **PayPal Disputes REST API**.

---

## 🎯 The Core Problem: The $100 Billion Friendly Fraud Drain

* **70%+ of Chargebacks are Friendly Fraud:** Consumers make legitimate purchases and subsequently claim *"I didn't authorize this"* or *"Package never arrived"*.
* **Heavy Operational Burden:** Merchants have 7–10 days to manually search through tracking numbers, customer emails, IP logs, and order histories to craft representment documents.
* **Complex Network Rules:** Card networks like Visa and Mastercard frequently update rules (e.g., Visa Compelling Evidence 3.0). SMB merchants rarely know how to leverage these rules to automatically shift liability back to the bank.
* **The "Unwinnable" Trap:** Fighting an unwinnable dispute costs merchants a non-refundable **$15–$25 dispute fee** and damages their dispute standing with PayPal.

---

## 💡 How ShieldAgent Solves It

ShieldAgent acts as an autonomous financial defense council with 4 specialized AI agents:

```
[ PayPal Dispute Webhook ] 
           │
           ▼
┌────────────────────────────────────────────────────────┐
│               Multi-Agent Defense Council              │
│                                                        │
│  1. Triage Agent: Evaluates win rate & financial ROI   │
│  2. Forensic Auditor: Cross-references carrier POD,    │
│     geolocations & inspects EXIF metadata              │
│  3. Compliance Agent: Automates Visa CE 3.0 & rules    │
│  4. Representment Agent: Generates defense dossier     │
└────────────────────────────────────────────────────────┘
           │
           ▼
[ Autonomous Execution ]
• Winnable: Submits evidence to PayPal Disputes API
• Unwinnable: Auto-concedes to save fees & avoid penalties
```

### The 4 Specialized Agents:
1. **Triage Agent (`app/agents/triage_agent.py`):**
   - Assesses dispute amount vs. dispute fees.
   - Calculates real-time **Win Probability (0–100%)** and net Expected Financial ROI.
   - Decides: `DEFEND` or `AUTO_CONCEDE`.

2. **Forensic Auditor Agent (`app/agents/forensic_agent.py`):**
   - Verifies Proof of Delivery (POD) via carrier APIs (FedEx, UPS, USPS).
   - Confirms delivery GPS coordinates and postal codes match buyer profile.
   - Audits image EXIF timestamps to flag fabricated or digitally tampered evidence.

3. **Compliance Agent (`app/agents/compliance_agent.py`):**
   - Implements **Visa Compelling Evidence 3.0 (CE 3.0)** rules for Reason Code 10.4.
   - Scans merchant databases for $\ge 2$ prior settled, undisputed transactions between 120 and 365 days old sharing matching IP, device ID, or shipping address.
   - **Guarantees automated liability shift** back to the issuing bank.

4. **Representment Agent (`app/agents/representment_agent.py`):**
   - Compiles findings into an official dispute defense dossier.
   - Formats the exact JSON payload required by PayPal's `/v1/customer/disputes/{id}/provide-evidence` endpoint.

---

## 🏗️ Project Structure

```
project/
├── .gitignore
├── README.md
├── docs/
│   ├── ARCHITECTURE.md                 # System diagrams, data flows, and design
│   └── DISPUTE_LIFECYCLE_&_CE30.md      # Deep dive into chargebacks, reason codes, & CE 3.0
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint
│   │   ├── core/                       # Settings, logging, and environment
│   │   ├── models/                     # Pydantic schemas for Disputes, Evidence, and Dossiers
│   │   ├── services/
│   │   │   ├── paypal_client.py        # PayPal Disputes REST API integration
│   │   │   └── tracking_service.py     # Carrier tracking lookup service
│   │   ├── agents/
│   │   │   ├── orchestrator.py         # Multi-agent coordination pipeline
│   │   │   ├── triage_agent.py         # ROI and Win Probability assessment
│   │   │   ├── forensic_agent.py       # Carrier POD and EXIF analysis
│   │   │   ├── compliance_agent.py     # Visa CE 3.0 & card network rules
│   │   │   └── representment_agent.py  # Dossier & PayPal API payload generator
│   │   └── api/
│   │       └── v1/
│   │           ├── webhooks.py         # PayPal webhook listener (CUSTOMER.DISPUTE.CREATED)
│   │           ├── disputes.py         # Dispute management endpoints
│   │           └── simulate.py         # Pre-configured test scenarios
│   └── tests/
│       └── test_pipeline.py            # End-to-end multi-agent pipeline tests
└── frontend/                           # Merchant Command Center Dashboard
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run automated tests
python tests/test_pipeline.py

# Start backend server
uvicorn app.main:app --reload --port 8000
```

The interactive API documentation (Swagger) will be available at `http://localhost:8000/docs`.

---

## 🧪 Interactive Simulations (Try it out!)

ShieldAgent comes with built-in realistic scenarios to test the agent council without waiting for real bank chargebacks:

| Endpoint | Scenario | Expected Agent Action |
| :--- | :--- | :--- |
| `POST /api/v1/simulate/friendly-fraud-inr` | Customer claims "Item Not Received", carrier confirms delivery with signature | **DEFEND** (Win Prob: 92%) |
| `POST /api/v1/simulate/visa-ce30-liability-shift` | Customer claims "Unauthorized", system locates 2 prior orders from 150 & 210 days ago | **DEFEND** (Liability Shift Guaranteed, Win Prob: 98%) |
| `POST /api/v1/simulate/unwinnable-micro-chargeback` | $12 dispute with no delivery proof | **AUTO_CONCEDE** (Saves \$20 fee and preserves merchant standing) |

---

## 👥 Hackathon Team Collaboration Notes

* **PayPal Sandbox:** Add your PayPal Sandbox Client ID & Secret to `backend/.env`.
* **Testing without PayPal:** The backend automatically falls back to safe Mock mode if PayPal credentials are not supplied, allowing offline UI and agent development.
* Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for sequence flows and agent details.

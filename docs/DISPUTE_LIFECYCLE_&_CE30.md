# Understanding Disputes, Friendly Fraud, and Visa CE 3.0

This guide provides the core domain knowledge behind **ShieldAgent**.

---

## 1. What is Friendly Fraud?

**Friendly Fraud** (also called "first-party fraud") occurs when a consumer makes a legitimate purchase with their own credit card or PayPal account, but later files a dispute with their issuing bank or PayPal claiming:
- *"I didn't authorize this payment"* (Unauthorized Transaction / Fraud code)
- *"The package never arrived"* (Item Not Received / INR)
- *"The item arrived completely damaged or not as described"* (Significantly Not As Described / SNAD)

### Why is Friendly Fraud a \$100B Problem?
1. **Asymmetric Friction:** Banking apps now allow cardholders to contest a charge with one tap.
2. **Merchant Loss Multiplier:** When a merchant loses a \$100 dispute, they lose:
   - The \$100 original sale
   - The wholesale cost of goods sold (COGS)
   - Shipping & fulfillment costs
   - A non-refundable **\$15–\$25 dispute fee** charged by the payment processor/network
   - Negative impact on the merchant's chargeback ratio (exceeding 0.9% can lead to account suspension or card network fines).

---

## 2. Card Network Rules: Visa Compelling Evidence 3.0 (CE 3.0)

Introduced in April 2023, **Visa CE 3.0** is the most powerful weapon against friendly fraud for code `10.4` (Other Fraud - Card-Absent Environment).

### The CE 3.0 Rule:
If a merchant can demonstrate that the customer previously made **at least two undisputed purchases** using the same payment credential (card), where:
1. Both prior transactions occurred between **120 days and 365 days** prior to the dispute date.
2. The disputed transaction shares at least **ONE** of the following core identifiers with both prior transactions:
   - **IP Address**
   - **Device ID / Fingerprint**
   - **Physical Shipping Address**

### The Result:
* Under Visa rules, proving CE 3.0 **shifts fraud liability back to the issuer immediately**.
* The merchant **wins the dispute automatically** before formal pre-arbitration.
* ShieldAgent's **Compliance Agent** automates this exact historical query in real time.

---

## 3. PayPal Disputes & Resolution Stages

PayPal classifies disputes into distinct phases:

```
[ INQUIRY / DISPUTE ] 
   └── Buyer opens dispute in PayPal Resolution Center.
   └── 20 days to communicate and resolve amicably.
         │
         ▼
[ CLAIM ]
   └── Escalated to PayPal to make a formal decision.
   └── Merchant has ~10 days to submit evidence.
         │
         ▼
[ CHARGEBACK ]
   └── Buyer contacted their credit card issuer directly (Visa, Mastercard, Amex).
   └── Card network rules apply. Merchant has strict 7–10 day SLA to provide representment.
```

ShieldAgent interfaces directly with PayPal's `/v1/customer/disputes` endpoints to automate evidence submission across all these stages.

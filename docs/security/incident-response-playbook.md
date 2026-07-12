# Incident response playbook

## Clocks

| Regime | Notification |
|---|---|
| GDPR Art.33 | **72 hours** to supervisory authority after awareness |
| VN PDPD (NĐ 13/2023) | follow Decree 13 breach notification timelines; treat **72h** as maximum when stricter is unclear |

## Steps

1. Detect (Sentry / Alertmanager) → severity.
2. Contain (revoke keys, open breakers — PLAT-008).
3. Eradicate + recover.
4. Notify DPO / counsel; log `audit_logs` fact of notification.
5. Post-mortem within 5 business days.

# Entity Graph Examples

Worked unification cases across the 7 entity types and 5 relation types.

## 1. Acronym ↔ expansion (merge)

"MFA" and "multi-factor authentication" — merge into one entity, both surface forms become `aliases`.

```json
{"id": "E-0001", "name": "Multi-factor authentication", "type": "control", "aliases": ["MFA"], "claims": ["C-0007", "C-0023"]}
```

## 2. Vendor + descriptor (merge)

"AWS Lambda" / "Lambda by AWS" — same product.

```json
{"id": "E-0002", "name": "AWS Lambda", "type": "service", "aliases": ["Lambda by AWS"], "claims": ["C-0011"]}
```

## 3. Versioned standards (keep separate, supersedes edge)

```json
{"id": "E-0010", "name": "OAuth 2.0", "type": "standard"}
{"id": "E-0011", "name": "OAuth 1.0", "type": "standard"}
{"from": "E-0010", "to": "E-0011", "relation": "supersedes", "claim_ids": ["C-0035"]}
```

## 4. Pattern ↔ implementation (instance_of)

"AWS Lambda is a FaaS offering."

```json
{"from": "E-0002", "to": "E-0030", "relation": "instance_of", "claim_ids": ["C-0040"]}
```

## 5. Conflict edge

"Service X requires us-east-1" + "Compliance requires EU residency."

```json
{"from": "E-0040", "to": "E-0041", "relation": "conflicts_with", "claim_ids": ["C-0050", "C-0051"]}
```

## 6. Pattern requires pattern

"Saga pattern requires idempotent operations."

```json
{"from": "E-0050", "to": "E-0051", "relation": "requires", "claim_ids": ["C-0060"]}
```

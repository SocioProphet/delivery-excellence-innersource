# delivery-excellence-innersource

InnerSource playbooks + repo readiness + portal/index spec.

## Professional Intelligence playbooks

This repo now carries validated playbook seeds for the Professional Intelligence OS alignment wave.

Playbooks live under:

- `playbooks/professional-intelligence/`

The schema lives at:

- `schemas/professional-intelligence-playbook.schema.json`

Validate playbooks with:

```bash
python3 -m pip install pyyaml jsonschema
python3 scripts/validate_professional_intelligence_playbooks.py
```

The GitHub Actions workflow `.github/workflows/professional-intelligence-playbooks.yml` runs this validation when playbooks, schema, validator, or workflow wiring change.

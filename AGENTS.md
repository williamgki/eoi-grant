# Repository layout

- `infra/` - Terraform infrastructure files
- `scripts/` - command line utilities and helpers
- `services/` - containerised services
- `portal/` - future user portal code

## Setup

Install tools:

```bash
$ tfenv use 1.6.3
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt
```

## Fast checks

```bash
$ ruff check
$ pytest
$ terraform fmt -check
$ terraform validate
```

## Apply infrastructure locally

```bash
$ cd infra && terraform init && terraform plan
```

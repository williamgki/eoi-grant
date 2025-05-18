init:
	@tfenv use 1.6.3
	python -m venv .venv && .venv/bin/pip install -r requirements.txt

plan:
	cd infra && terraform init && terraform plan

apply:
	cd infra && terraform init && terraform apply

docker:
	docker build -t eoi-scorer -f services/scorer/Dockerfile .

test:
	.venv/bin/pytest

lint:
	.venv/bin/ruff check
	terraform fmt -check infra
	terraform validate infra

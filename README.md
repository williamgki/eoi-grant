# Alignment Grants Infrastructure

This repository contains the Terraform configuration used to provision the cloud resources required by the Expression of Interest (EOI) grant pipeline.  It acts as the infrastructure-as-code component of the wider EOI workflow, ensuring that the AWS environment is reproducible and version-controlled.

## Prerequisites

- **Terraform**: The project uses Terraform `1.6.3` (see `.terraform-version`). Ensure this version is installed, or use a version manager such as [tfenv](https://github.com/tfutils/tfenv).
- **AWS credentials**: Terraform authenticates with AWS using the same credentials as the AWS CLI. Configure your AWS account by setting environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and optionally `AWS_SESSION_TOKEN`) or by using an AWS credentials file.
- **AWS CLI** (optional but recommended) for managing profiles and verifying credentials.

## Usage

The Terraform code resides in the `infra/` directory. Run the following commands from that directory:

```bash
cd infra
terraform init    # Download providers and set up the backend
terraform plan    # Review the changes
terraform apply   # Apply the changes after confirmation
```

A typical workflow is to run `terraform plan -out=tfplan` and then `terraform apply tfplan` when you are satisfied with the plan.

## Repository purpose within the EOI grant pipeline

This repository defines and manages the infrastructure that supports the Alignment Grants EOI process. The Terraform configuration sets up the AWS resources—such as storage, compute, and permissions—that other parts of the pipeline rely on. By keeping the infrastructure definition here, any environment used for the EOI grants can be recreated consistently and tracked through version control.

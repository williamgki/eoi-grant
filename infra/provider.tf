terraform {
  required_version = "~> 1.6.3"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"          # London
  # Uses the same creds the CLI already has
}

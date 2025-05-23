variable "scorer_image" {
  description = "Container image for the scorer task"
  type        = string
}

variable "scorer_schedule" {
  description = "Cron or rate expression for running the scorer"
  type        = string
  default     = "rate(2 minutes)"
}

variable "openai_api_key_secret_id" {
  description = "Secrets Manager ID storing the OpenAI API key"
  type        = string
}

variable "database_url" {
  description = "Database connection string for the scorer"
  type        = string
}

variable "portal_bucket_name" {
  description = "Name for the portal static site bucket"
  type        = string
}

variable "log_export_bucket" {
  description = "S3 bucket name for exporting CloudWatch logs"
  type        = string
}

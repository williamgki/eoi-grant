variable "scorer_image" {
  description = "Container image for the scorer task"
  type        = string
}

variable "scorer_schedule" {
  description = "Cron or rate expression for running the scorer"
  type        = string
  default     = "rate(5 minutes)"
}

variable "openai_api_key_secret_id" {
  description = "Secrets Manager ID storing the OpenAI API key"
  type        = string
}

variable "database_url" {
  description = "Database connection string for the scorer"
  type        = string
}

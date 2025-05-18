variable "log_export_bucket" {
  description = "Bucket for CloudWatch log exports"
  type        = string
}

resource "aws_cloudwatch_log_group" "eoi_scorer" {
  name              = "/ecs/eoi-scorer"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "email_draft" {
  name              = "/ecs/email-draft"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "eoi_scorer" {
  name              = "/ecs/eoi-scorer"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "email_draft" {
  name              = "/ecs/email-draft"
  retention_in_days = 90
}

# Bucket for exporting CloudWatch logs
resource "aws_s3_bucket" "log_export" {
  bucket        = var.log_export_bucket
  force_destroy = true
}

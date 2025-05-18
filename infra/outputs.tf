locals {
  queue_url   = aws_sqs_queue.ingest.url
  db_endpoint = aws_rds_cluster.eoi_app.endpoint
}

output "queue_url" {
  value = local.queue_url
}

output "db_endpoint" {
  value = local.db_endpoint
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "portal_url" {
  value = aws_s3_bucket_website_configuration.portal.website_endpoint
}

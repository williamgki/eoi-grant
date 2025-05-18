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

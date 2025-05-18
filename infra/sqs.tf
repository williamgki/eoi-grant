resource "aws_sqs_queue" "ingest_dlq" {
  name       = "eoi-ingest-dlq.fifo"
  fifo_queue = true
}

resource "aws_sqs_queue" "ingest" {
  name                       = "eoi-ingest.fifo"
  fifo_queue                 = true
  content_based_deduplication = true
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.ingest_dlq.arn
    maxReceiveCount     = 5
  })
}

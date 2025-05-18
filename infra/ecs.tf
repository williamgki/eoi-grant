resource "aws_ecs_cluster" "main" {
  name = "eoi-cluster"

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
  }
}

resource "aws_ecs_task_definition" "scorer" {
  family                   = "eoi-scorer"
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "scorer"
      image     = var.scorer_image
      essential = true
      environment = [
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.ingest.url }
      ]
      secrets = [
        { name = "OPENAI_API_KEY", valueFrom = var.openai_api_key_secret_id },
        { name = "DATABASE_URL", valueFrom = var.database_url }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.eoi_scorer.name
          awslogs-region        = "eu-west-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_cloudwatch_event_rule" "scorer_schedule" {
  name                = "eoi-scorer-schedule"
  schedule_expression = var.scorer_schedule
}

resource "aws_cloudwatch_event_target" "scorer_target" {
  rule      = aws_cloudwatch_event_rule.scorer_schedule.name
  target_id = "scorer"
  arn       = aws_ecs_cluster.main.arn

  ecs_target {
    launch_type         = "FARGATE"
    task_definition_arn = aws_ecs_task_definition.scorer.arn
    network_configuration {
      subnets         = data.aws_subnets.default.ids
      security_groups = [data.aws_default_vpc.default.default_security_group_id]
    }
    platform_version = "LATEST"
    task_count       = 1
  }
  role_arn = aws_iam_role.events.arn
}

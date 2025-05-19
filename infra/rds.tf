data "aws_default_vpc" "default" {}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_default_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "default"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_rds_cluster" "eoi_app" {
  engine                  = "aurora-mysql"
  database_name           = "eoi_app"
  db_subnet_group_name    = aws_db_subnet_group.default.name
  vpc_security_group_ids  = [data.aws_default_vpc.default.default_security_group_id]

  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 4
  }
}


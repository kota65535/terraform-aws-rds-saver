terraform {
  backend "s3" {
    bucket = "terraform-backend-561678142736"
    region = "ap-northeast-1"
    key    = "terraform-aws-rds-saver.tfstate"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.52.0"
    }
  }
  required_version = "~> 1.4.0"
}

provider "aws" {
  region = "ap-northeast-1"
}

module "rds_saver" {
  source = "../../"
}

resource "aws_rds_cluster" "main" {
  cluster_identifier   = "test"
  engine               = "aurora-mysql"
  engine_version       = "8.0.mysql_aurora.3.02.0"
  engine_mode          = "provisioned"
  master_username      = "root"
  db_subnet_group_name = aws_db_subnet_group.main.name

  serverlessv2_scaling_configuration {
    min_capacity = 1
    max_capacity = 2
  }
  apply_immediately = true
  tags = {
    AutoStartTime = 10
    AutoStopTime  = 11
  }
}

resource "aws_db_instance" "main" {
  identifier           = "test2"
  engine               = "mysql"
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  allocated_storage    = 5
  username             = "root"
  password             = "rootroot"
  db_subnet_group_name = aws_db_subnet_group.main.name
  apply_immediately    = true
  tags = {
    AutoStartTime = 10
    AutoStopTime  = 11
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "test"
  subnet_ids = ["subnet-0abaada26acb8894f", "subnet-0ef9f8fc78d0642d8"]
  tags = {
    Name = "test"
  }
}

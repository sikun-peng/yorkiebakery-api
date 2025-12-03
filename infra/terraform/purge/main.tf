terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  lambda_name    = var.lambda_name
  log_group_name = "/aws/lambda/${local.lambda_name}"
}

resource "null_resource" "build_lambda" {
  # Rebuild when source or requirements change
  triggers = {
    handler_hash      = filesha256("${path.module}/lambda/handler.py")
    requirements_hash = filesha256("${path.module}/lambda/requirements.txt")
  }

  provisioner "local-exec" {
    command = <<-EOT
      set -euo pipefail
      BUILD_DIR="${path.module}/lambda/build"
      rm -rf "$BUILD_DIR"
      mkdir -p "$BUILD_DIR"
      python3 -m venv "$BUILD_DIR/.venv"
      . "$BUILD_DIR/.venv/bin/activate"
      python -m pip install --upgrade pip
      pip install -r "${path.module}/lambda/requirements.txt" -t "$BUILD_DIR"
      cp "${path.module}/lambda/handler.py" "$BUILD_DIR/"
      deactivate
      rm -rf "$BUILD_DIR/.venv"
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.build_lambda]
  type        = "zip"
  source_dir  = "${path.module}/lambda/build"
  output_path = "${path.module}/lambda/function.zip"
}

resource "aws_iam_role" "lambda_role" {
  name               = "${local.lambda_name}-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    sid    = "AllowLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"]
  }

  statement {
    sid     = "ReadDbSecret"
    effect  = "Allow"
    actions = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParameterHistory"]
    resources = [
      "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter${var.database_url_ssm_param}"
    ]
  }

  dynamic "statement" {
    for_each = var.vpc_subnet_ids == null ? [] : [1]
    content {
      sid    = "ENI"
      effect = "Allow"
      actions = [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ]
      resources = ["*"]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role_policy" "lambda_policy" {
  name   = "${local.lambda_name}-policy"
  role   = aws_iam_role.lambda_role.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = local.log_group_name
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "purge" {
  function_name = local.lambda_name
  role          = aws_iam_role.lambda_role.arn
  handler       = "handler.handler"
  runtime       = "python3.11"
  memory_size   = 256
  timeout       = 10

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      DB_PARAM_NAME = var.database_url_ssm_param
      GRACE_SECONDS = var.grace_period_seconds
    }
  }

  dynamic "vpc_config" {
    for_each = var.vpc_subnet_ids == null ? [] : [1]
    content {
      subnet_ids         = var.vpc_subnet_ids
      security_group_ids = var.vpc_security_group_ids
    }
  }
}

resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "${local.lambda_name}-schedule"
  description         = "Daily purge of unverified users older than grace period"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "schedule_target" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "lambda"
  arn       = aws_lambda_function.purge.arn
}

resource "aws_lambda_permission" "allow_events" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.purge.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule.arn
}

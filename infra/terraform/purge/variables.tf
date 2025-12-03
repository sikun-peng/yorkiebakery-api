variable "aws_region" {
  type        = string
  description = "AWS region to deploy the purge Lambda."
  default     = "us-west-2"
}

variable "lambda_name" {
  type        = string
  description = "Name for the purge Lambda function."
  default     = "purge-unverified-users"
}

variable "database_url_ssm_param" {
  type        = string
  description = "SSM parameter name that stores the DATABASE_URL for the app (e.g., /yorkiebakery/prod/DATABASE_URL)."
}

variable "grace_period_seconds" {
  type        = string
  description = "Seconds after account creation before purge; string to avoid type coercion in Lambda env."
  default     = "86400"
}

variable "schedule_expression" {
  type        = string
  description = "EventBridge schedule expression, e.g., cron(0 9 * * ? *) for daily 09:00 UTC."
  default     = "cron(0 9 * * ? *)"
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention for the Lambda."
  default     = 14
}

variable "vpc_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for the Lambda ENIs (if DB is inside a VPC). Leave null to run without VPC."
  default     = null
}

variable "vpc_security_group_ids" {
  type        = list(string)
  description = "Security group IDs for the Lambda ENIs (if DB is inside a VPC). Required when vpc_subnet_ids is set."
  default     = []
}

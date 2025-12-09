variable "aws_region" {
  description = "AWS region to deploy the uptime check"
  type        = string
  default     = "us-west-2"
}

variable "health_url" {
  description = "URL to check for uptime (e.g., https://yorkiebakery.com/health)"
  type        = string
}

variable "schedule_expression" {
  description = "EventBridge schedule expression"
  type        = string
  default     = "rate(30 minutes)"
}

variable "alert_email" {
  description = "Email address for SNS alerts (leave blank to skip subscription)"
  type        = string
  default     = ""
}

variable "name" {
  description = "Base name for resources"
  type        = string
  default     = "yorkiebakery-uptime"
}

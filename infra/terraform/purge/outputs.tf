output "lambda_name" {
  value       = aws_lambda_function.purge.function_name
  description = "Name of the purge Lambda."
}

output "eventbridge_rule_arn" {
  value       = aws_cloudwatch_event_rule.schedule.arn
  description = "ARN of the scheduled EventBridge rule."
}

# Purge unverified users (Terraform)

Adds a scheduled Lambda that deletes unverified accounts older than a grace period, without touching the existing EC2/docker deploy loop.

## What this does
- Provisions a Python 3.11 Lambda packaged with `pg8000` (pure-Python Postgres driver).
- Pulls the database URL from SSM at runtime (`DB_PARAM_NAME` env).
- Deletes users where `is_verified = false` and `created_at` is older than `GRACE_SECONDS` (default 24h).
- Runs daily via EventBridge (default cron: `0 9 * * ? *`).
- Optional VPC configuration for RDS/private DBs.

## Inputs to set
- `aws_region`: AWS region.
- `database_url_ssm_param`: SSM parameter name that holds `DATABASE_URL` (e.g., `/yorkiebakery/prod/DATABASE_URL`). Lambda reads it at runtime; the secret is not stored in state.
- `grace_period_seconds`: purge threshold in seconds (default 86400).
- `schedule_expression`: EventBridge cron/rate expression (default daily 09:00 UTC).
- Optional: `vpc_subnet_ids` and `vpc_security_group_ids` if the DB is inside a VPC.

## Build/package behavior
Terraform uses `null_resource` + `archive_file` to:
- `pip install` dependencies into `lambda/build`
- zip that folder for the Lambda code

You need local Python 3.11 and internet to fetch wheels when running `terraform apply`.

## Usage
```bash
cd infra/terraform/purge
terraform init
terraform plan -var="database_url_ssm_param=/yorkiebakery/prod/DATABASE_URL"
# Optional: -var="vpc_subnet_ids=[\"subnet-abc\",\"subnet-def\"]" -var="vpc_security_group_ids=[\"sg-123\"]"
terraform apply -var="database_url_ssm_param=/yorkiebakery/prod/DATABASE_URL"
```

## Notes
- Keep the SSM parameter encrypted (SecureString) and ensure the Lambda role can `ssm:GetParameter` on it.
- If the DB is in a VPC, supply private subnets and a security group with egress to Postgres.
- Logs are written to CloudWatch Logs with retention configurable via `log_retention_days` (default 14).
- This is additive; it does not modify your existing EC2/docker deployment.***

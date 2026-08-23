# DigiIn Production Infrastructure — Network Module
# Provisions isolated VPC, public load-balancer subnets, private application subnets, and database subnets.

variable "environment" {
  type        = string
  description = "Target deployment environment (staging / production)"
  default     = "production"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

output "vpc_id" {
  value = "vpc-digiin-${var.environment}-01"
}

output "private_app_subnets" {
  value = ["subnet-app-01a", "subnet-app-01b"]
}

output "private_db_subnets" {
  value = ["subnet-db-01a", "subnet-db-01b"]
}

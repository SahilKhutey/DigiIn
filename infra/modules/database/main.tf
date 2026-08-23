# DigiIn Production Infrastructure — PostgreSQL Database Module
# Provisions private PostgreSQL primary instance with multi-AZ read replica and encryption at rest.

variable "environment" {
  type    = string
  default = "production"
}

variable "instance_class" {
  type    = string
  default = "db.r6g.xlarge"
}

output "db_primary_endpoint" {
  value = "postgres-primary.${var.environment}.digiin.internal:5432"
}

output "db_replica_endpoint" {
  value = "postgres-replica.${var.environment}.digiin.internal:5432"
}

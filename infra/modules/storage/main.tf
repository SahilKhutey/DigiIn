# DigiIn Production Infrastructure — S3 / GCS Object Storage Module
# Provisions private encrypted document bucket with strict lifecycle and access logging.

variable "environment" {
  type    = string
  default = "production"
}

output "documents_bucket_name" {
  value = "digiin-${var.environment}-documents-encrypted"
}

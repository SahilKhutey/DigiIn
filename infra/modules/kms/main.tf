# DigiIn Production Infrastructure — Cloud KMS Keyring Module
# Provisions master cryptographic keyrings for envelope encryption and HSM-backed digital signing.

variable "environment" {
  type    = string
  default = "production"
}

output "kms_master_key_id" {
  value = "projects/digiin-${var.environment}/locations/asia-south1/keyRings/digiin-ring/cryptoKeys/master"
}

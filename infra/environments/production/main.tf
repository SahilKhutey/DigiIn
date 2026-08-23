# DigiIn Production Environment Configuration
terraform {
  required_version = ">= 1.5.0"
}

module "network" {
  source      = "../../modules/network"
  environment = "production"
}

module "database" {
  source      = "../../modules/database"
  environment = "production"
}

module "storage" {
  source      = "../../modules/storage"
  environment = "production"
}

module "kms" {
  source      = "../../modules/kms"
  environment = "production"
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resource deployment"
  type        = string
  default     = "us-east1"
}

variable "zone" {
  description = "GCP zone for compute resources"
  type        = string
  default     = "us-east1-b"
}

variable "vm_name" {
  description = "Name of the compute instance"
  type        = string
  default     = "shivang-terraform-vm"
}

variable "machine_type" {
  description = "Machine type for the VM instance"
  type        = string
  default     = "e2-micro"
}

variable "vm_image" {
  description = "OS image for the boot disk"
  type        = string
  default     = "ubuntu-os-cloud/ubuntu-2204-lts"
}

variable "boot_disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 10
}

variable "bucket_name" {
  description = "Name of the GCS bucket (must be globally unique)"
  type        = string
  default     = "shivang-terraform-lab-bucket-2026"
}

variable "environment" {
  description = "Environment label for resources"
  type        = string
  default     = "development"
}
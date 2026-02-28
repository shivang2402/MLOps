terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "vm_instance" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone

  labels = {
    environment = var.environment
    owner       = "shivang"
    managed_by  = "terraform"
  }

  boot_disk {
    initialize_params {
      image = var.vm_image
      size  = var.boot_disk_size
    }
  }

  network_interface {
    network = "default"

    access_config {
    }
  }

  metadata = {
    startup_script = "#!/bin/bash\napt-get update\napt-get install -y nginx"
  }
}

resource "google_storage_bucket" "lab_bucket" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true
  storage_class = "STANDARD"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}
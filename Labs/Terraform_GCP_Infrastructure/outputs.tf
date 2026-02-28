output "vm_name" {
  description = "Name of the created VM instance"
  value       = google_compute_instance.vm_instance.name
}

output "vm_external_ip" {
  description = "External IP address of the VM"
  value       = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}

output "vm_internal_ip" {
  description = "Internal IP address of the VM"
  value       = google_compute_instance.vm_instance.network_interface[0].network_ip
}

output "bucket_name" {
  description = "Name of the GCS bucket"
  value       = google_storage_bucket.lab_bucket.name
}

output "bucket_url" {
  description = "URL of the GCS bucket"
  value       = google_storage_bucket.lab_bucket.url
}
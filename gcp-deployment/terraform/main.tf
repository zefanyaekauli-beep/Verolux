# Verolux Enterprise - Main Terraform Configuration
# Complete GCP infrastructure with all features

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "verolux-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "storage-api.googleapis.com",
    "sqladmin.googleapis.com",
    "secretmanager.googleapis.com",
    "containerregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  service = each.key
  disable_on_destroy = false
}

# Service Account
resource "google_service_account" "verolux_sa" {
  account_id   = "verolux-sa"
  display_name = "Verolux Service Account"
  description  = "Service account for Verolux Enterprise system"
}

# IAM Bindings
resource "google_project_iam_member" "verolux_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.verolux_sa.email}"
}

resource "google_project_iam_member" "verolux_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.verolux_sa.email}"
}

resource "google_project_iam_member" "verolux_secrets" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.verolux_sa.email}"
}

resource "google_project_iam_member" "verolux_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.verolux_sa.email}"
}

resource "google_project_iam_member" "verolux_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.verolux_sa.email}"
}

# GPU Compute Instance
resource "google_compute_instance" "verolux_gpu" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "deeplearning-platform-release/pytorch-latest-gpu"
      size  = var.disk_size
      type  = "pd-ssd"
    }
  }

  guest_accelerator {
    type  = var.gpu_type
    count = var.gpu_count
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = file("${path.module}/../scripts/startup-script.sh")

  scheduling {
    on_host_maintenance = "TERMINATE"
    automatic_restart   = true
  }

  service_account {
    email  = google_service_account.verolux_sa.email
    scopes = ["cloud-platform"]
  }

  tags = ["verolux", "http-server", "https-server"]

  labels = {
    environment = var.environment
    application = "verolux-enterprise"
    component   = "gpu-inference"
  }
}

# Firewall Rules
resource "google_compute_firewall" "verolux_http" {
  name    = "verolux-http"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server", "https-server"]
  
  description = "Allow HTTP/HTTPS traffic to Verolux frontend"
}

resource "google_compute_firewall" "verolux_api" {
  name    = "verolux-api"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8000", "8001", "8002", "8003", "8004", "8005"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["verolux"]
  
  description = "Allow API traffic to Verolux backend services"
}

resource "google_compute_firewall" "verolux_ssh" {
  name    = "verolux-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = var.ssh_source_ranges
  target_tags   = ["verolux"]
  
  description = "Allow SSH access to Verolux instances"
}

# Cloud Storage Bucket
resource "google_storage_bucket" "verolux_storage" {
  name          = "${var.project_id}-verolux-storage"
  location      = var.region
  storage_class = "STANDARD"
  
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
    application = "verolux-enterprise"
  }
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "verolux_db" {
  name             = "verolux-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = var.db_availability_type

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "verolux-instance"
        value = google_compute_instance.verolux_gpu.network_interface[0].access_config[0].nat_ip
      }
    }

    database_flags {
      name  = "max_connections"
      value = "200"
    }

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
      }
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
  }

  deletion_protection = var.db_deletion_protection
}

# Databases
resource "google_sql_database" "verolux_enterprise" {
  name     = "verolux_enterprise"
  instance = google_sql_database_instance.verolux_db.name
}

resource "google_sql_database" "verolux_analytics" {
  name     = "verolux_analytics"
  instance = google_sql_database_instance.verolux_db.name
}

# Database User
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_sql_user" "postgres" {
  name     = "postgres"
  instance = google_sql_database_instance.verolux_db.name
  password = random_password.db_password.result
}

# Secret Manager - DB Password
resource "google_secret_manager_secret" "db_password" {
  secret_id = "verolux-db-password"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Grant access to secrets
resource "google_secret_manager_secret_iam_member" "db_password_access" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.verolux_sa.email}"
}

# Cloud Monitoring - Uptime Check
resource "google_monitoring_uptime_check_config" "verolux_backend" {
  display_name = "Verolux Backend Health Check"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/health"
    port         = "8000"
    request_method = "GET"
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_compute_instance.verolux_gpu.network_interface[0].access_config[0].nat_ip
    }
  }
}

# Cloud Monitoring - Alert Policy (GPU Utilization)
resource "google_monitoring_alert_policy" "gpu_utilization" {
  display_name = "Verolux - High GPU Utilization"
  combiner     = "OR"
  
  conditions {
    display_name = "GPU utilization above 90%"
    
    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND metric.type=\"compute.googleapis.com/instance/accelerator/gpu_utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.9
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.notification_channels

  documentation {
    content = "GPU utilization is above 90% for 5 minutes. Consider scaling or optimizing workload."
  }
}

# Cloud Monitoring - Alert Policy (API Errors)
resource "google_monitoring_alert_policy" "api_errors" {
  display_name = "Verolux - High API Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "API error rate above 5%"
    
    condition_threshold {
      filter          = "resource.type=\"gce_instance\" AND metric.type=\"logging.googleapis.com/user/api_error_rate\""
      duration        = "180s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.notification_channels

  documentation {
    content = "API error rate is above 5%. Check application logs for details."
  }
}

# Outputs
output "instance_name" {
  value       = google_compute_instance.verolux_gpu.name
  description = "Name of the GPU compute instance"
}

output "instance_ip" {
  value       = google_compute_instance.verolux_gpu.network_interface[0].access_config[0].nat_ip
  description = "External IP address of the instance"
}

output "instance_zone" {
  value       = google_compute_instance.verolux_gpu.zone
  description = "Zone where instance is deployed"
}

output "storage_bucket" {
  value       = google_storage_bucket.verolux_storage.name
  description = "Cloud Storage bucket name"
}

output "database_connection" {
  value       = google_sql_database_instance.verolux_db.connection_name
  description = "Cloud SQL connection name"
}

output "database_ip" {
  value       = google_sql_database_instance.verolux_db.ip_address[0].ip_address
  description = "Cloud SQL IP address"
}

output "service_account_email" {
  value       = google_service_account.verolux_sa.email
  description = "Service account email"
}

output "frontend_url" {
  value       = "http://${google_compute_instance.verolux_gpu.network_interface[0].access_config[0].nat_ip}"
  description = "Frontend URL"
}

output "backend_api_url" {
  value       = "http://${google_compute_instance.verolux_gpu.network_interface[0].access_config[0].nat_ip}:8000"
  description = "Backend API URL"
}


















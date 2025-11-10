# Verolux Enterprise - Terraform Variables

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "asia-southeast2" # Jakarta
}

variable "zone" {
  description = "GCP zone for compute resources"
  type        = string
  default     = "asia-southeast2-a"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

# Compute Instance Variables
variable "instance_name" {
  description = "Name of the GPU compute instance"
  type        = string
  default     = "verolux-gpu-instance"
}

variable "machine_type" {
  description = "Machine type for compute instance"
  type        = string
  default     = "g2-standard-8"
  
  validation {
    condition     = can(regex("^g2-standard-(4|8|16|32|48|96)$", var.machine_type))
    error_message = "Machine type must be a valid G2 instance type (g2-standard-4/8/16/32/48/96)"
  }
}

variable "gpu_type" {
  description = "GPU accelerator type"
  type        = string
  default     = "nvidia-l4"
  
  validation {
    condition     = contains(["nvidia-l4", "nvidia-tesla-t4", "nvidia-tesla-v100", "nvidia-tesla-a100"], var.gpu_type)
    error_message = "GPU type must be one of: nvidia-l4, nvidia-tesla-t4, nvidia-tesla-v100, nvidia-tesla-a100"
  }
}

variable "gpu_count" {
  description = "Number of GPUs to attach"
  type        = number
  default     = 1
  
  validation {
    condition     = var.gpu_count >= 1 && var.gpu_count <= 8
    error_message = "GPU count must be between 1 and 8"
  }
}

variable "disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 100
  
  validation {
    condition     = var.disk_size >= 50 && var.disk_size <= 1000
    error_message = "Disk size must be between 50 and 1000 GB"
  }
}

# Database Variables
variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-2-7680" # 2 vCPU, 7.5 GB RAM
}

variable "db_availability_type" {
  description = "Cloud SQL availability type (ZONAL or REGIONAL)"
  type        = string
  default     = "ZONAL"
  
  validation {
    condition     = contains(["ZONAL", "REGIONAL"], var.db_availability_type)
    error_message = "Availability type must be ZONAL or REGIONAL"
  }
}

variable "db_deletion_protection" {
  description = "Enable deletion protection for database"
  type        = bool
  default     = true
}

# Network Variables
variable "ssh_source_ranges" {
  description = "Source IP ranges allowed to SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"] # Change to your IP range for production
}

# Monitoring Variables
variable "notification_channels" {
  description = "Notification channels for alerts"
  type        = list(string)
  default     = []
}

# Storage Variables
variable "storage_retention_days" {
  description = "Number of days to retain video data"
  type        = number
  default     = 90
  
  validation {
    condition     = var.storage_retention_days >= 7 && var.storage_retention_days <= 365
    error_message = "Storage retention must be between 7 and 365 days"
  }
}

# Application Variables
variable "batch_size" {
  description = "YOLO inference batch size"
  type        = number
  default     = 4
}

variable "substream_scale" {
  description = "Detection substream scale (0.1-1.0)"
  type        = number
  default     = 0.6
  
  validation {
    condition     = var.substream_scale >= 0.1 && var.substream_scale <= 1.0
    error_message = "Substream scale must be between 0.1 and 1.0"
  }
}

variable "target_fps" {
  description = "Target inference FPS"
  type        = number
  default     = 30
}

# Cost Optimization
variable "use_preemptible" {
  description = "Use preemptible instances (dev/test only)"
  type        = bool
  default     = false
}

variable "auto_shutdown_enabled" {
  description = "Enable automatic shutdown during off-hours"
  type        = bool
  default     = false
}

variable "auto_shutdown_schedule" {
  description = "Cron schedule for automatic shutdown (if enabled)"
  type        = string
  default     = "0 20 * * *" # 8 PM daily
}

# Tags and Labels
variable "tags" {
  description = "Additional network tags for the instance"
  type        = list(string)
  default     = []
}

variable "labels" {
  description = "Additional labels for resources"
  type        = map(string)
  default     = {}
}
























variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "911-call-generator"
}

# Image Configuration
variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "image_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8080
}

# Network Configuration
variable "vpc_id" {
  description = "VPC ID where App Runner will connect"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for VPC connector"
  type        = list(string)
}

# Domain Configuration (Optional)
variable "domain_zone" {
  description = "Route53 hosted zone name for custom domain (optional)"
  type        = string
  default     = ""
}

variable "domain_subdomain" {
  description = "Subdomain for the application (optional)"
  type        = string
  default     = ""
}

# Resource Configuration
variable "cpu" {
  description = "vCPU units (0.25, 0.5, 1, 2, 4)"
  type        = number
  default     = 1
}

variable "memory" {
  description = "Memory in GB (0.5, 1, 2, 3, 4, 6, 8, 10, 12)"
  type        = number
  default     = 2
}

# Scaling Configuration
variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 5
}

# Health Check Configuration
variable "health_check_path" {
  description = "Health check path"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 10
}

variable "health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

# Secrets Configuration
variable "gemini_api_key_secret_arn" {
  description = "ARN of AWS Secrets Manager secret containing Gemini API key"
  type        = string
}

variable "elevenlabs_api_key_secret_arn" {
  description = "ARN of AWS Secrets Manager secret containing ElevenLabs API key"
  type        = string
}

# Tags
variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}

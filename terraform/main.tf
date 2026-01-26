# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local variables
locals {
  app_name            = "${var.environment}-${var.app_name}"
  ecr_repository_name = var.app_name
  use_custom_domain   = var.domain_zone != "" && var.domain_subdomain != ""
}

# Create App Runner service role (reusable for multiple services)
module "app_runner_service_role" {
  source = "../../jagger/terraform/modules/app-runner/service_role"

  env  = var.environment
  tags = var.tags
}

# Create the 911 Call Generator App Runner service
module "call_generator" {
  source = "../../jagger/terraform/modules/app-runner"

  name = var.app_name
  env  = var.environment

  # Image configuration
  image = {
    name     = local.ecr_repository_name
    tag      = var.image_tag
    port     = var.image_port
    base_url = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.region}.amazonaws.com"
  }

  # Network configuration
  network = {
    vpc     = var.vpc_id
    subnets = var.private_subnet_ids
  }

  # Domain configuration (if provided)
  domain = local.use_custom_domain ? {
    zone      = var.domain_zone
    subdomain = var.domain_subdomain
  } : null

  # Resource configuration
  resources = {
    cpu    = var.cpu
    memory = var.memory
  }

  # Scaling configuration
  scaling = {
    min = var.min_instances
    max = var.max_instances
  }

  # Health check configuration
  probes = {
    path                = var.health_check_path
    interval            = var.health_check_interval
    timeout             = var.health_check_timeout
    healthy_threshold   = 1
    unhealthy_threshold = 3
  }

  # Environment variables
  env_vars = {
    FLASK_ENV          = var.environment
    MAX_PROMPT_LENGTH  = "500"
    LOG_LEVEL          = var.environment == "prod" ? "INFO" : "DEBUG"
  }

  # Secrets from AWS Secrets Manager
  secrets = {
    GEMINI_API_KEY     = var.gemini_api_key_secret_arn
    ELEVENLABS_API_KEY = var.elevenlabs_api_key_secret_arn
  }

  # Firewall rules for VPC connector
  firewall = {
    # Allow HTTPS egress for API calls
    egress = {
      https = {
        to       = ["0.0.0.0/0"]
        port     = 443
        protocol = "tcp"
      }
      http = {
        to       = ["0.0.0.0/0"]
        port     = 80
        protocol = "tcp"
      }
    }
  }

  # IAM permissions (if needed for S3, DynamoDB, etc.)
  permissions = {
    # Example: If you need S3 access for audio storage
    # buckets = {
    #   read  = ["arn:aws:s3:::my-audio-bucket/*"]
    #   write = ["arn:aws:s3:::my-audio-bucket/*"]
    # }
  }

  # Use the service role created above
  service_role_arn = module.app_runner_service_role.arn

  tags = merge(var.tags, {
    Application = "911-call-generator"
    Component   = "web-service"
  })
}

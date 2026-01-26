output "service_url" {
  description = "URL of the App Runner service"
  value       = module.call_generator.service.service_url
}

output "service_id" {
  description = "ID of the App Runner service"
  value       = module.call_generator.service.service_id
}

output "service_arn" {
  description = "ARN of the App Runner service"
  value       = module.call_generator.service.arn
}

output "service_status" {
  description = "Current status of the App Runner service"
  value       = module.call_generator.service.status
}

output "custom_domain" {
  description = "Custom domain configuration (if configured)"
  value = local.use_custom_domain ? {
    domain = "${var.domain_subdomain}.${var.domain_zone}"
    status = "Check Route53 for DNS validation records"
  } : null
}

output "vpc_connector_arn" {
  description = "ARN of the VPC connector"
  value       = module.call_generator.vpc_connector.arn
}

output "service_role_arn" {
  description = "ARN of the App Runner service role"
  value       = module.app_runner_service_role.arn
}

output "ecr_repository" {
  description = "ECR repository information"
  value = {
    name = local.ecr_repository_name
    uri  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.region}.amazonaws.com/${local.ecr_repository_name}"
  }
}

output "deployment_info" {
  description = "Deployment information"
  value = {
    environment    = var.environment
    app_name       = local.app_name
    image_tag      = var.image_tag
    region         = data.aws_region.current.region
    min_instances  = var.min_instances
    max_instances  = var.max_instances
    cpu            = var.cpu
    memory         = var.memory
  }
}

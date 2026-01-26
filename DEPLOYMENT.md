# 911 Call Generator - Deployment Guide

This guide walks through deploying the 911 Call Generator application to AWS App Runner using Terraform.

## Architecture Overview

The deployment uses:
- **AWS App Runner**: Fully managed container service for running the Flask application
- **Amazon ECR**: Docker image registry
- **AWS Secrets Manager**: Secure storage for API keys
- **VPC Integration**: Private networking with VPC connector
- **Route53** (optional): Custom domain configuration
- **Terraform**: Infrastructure as Code for reproducible deployments

## Prerequisites

### Required Tools

1. **Docker Desktop**
   ```bash
   # Install from: https://docs.docker.com/get-docker/
   docker --version  # Verify installation
   ```

2. **AWS CLI v2**
   ```bash
   # Install from: https://aws.amazon.com/cli/
   aws --version  # Verify installation
   aws configure  # Configure credentials
   ```

3. **Terraform**
   ```bash
   # Install from: https://www.terraform.io/downloads
   terraform --version  # Verify installation (>= 1.13.0)
   ```

### AWS Prerequisites

1. **VPC Setup**
   - Existing VPC with at least 2 private subnets in different availability zones
   - NAT Gateway configured for private subnets (for external API access)

2. **AWS Permissions**
   - IAM permissions to create:
     - App Runner services
     - ECR repositories
     - Secrets Manager secrets
     - IAM roles and policies
     - VPC connectors and endpoints
     - Route53 records (if using custom domain)

3. **jagger Repository**
   - Clone the RapidSOS jagger repo (contains the App Runner Terraform module):
     ```bash
     cd /Users/cfucci/Desktop
     git clone https://github.com/RapidSOS/jagger.git
     ```
   - Ensure the path matches the module source in `terraform/main.tf`

## Deployment Steps

### Step 1: Clone and Navigate

```bash
cd /Users/cfucci/Desktop/911-call-generator
```

### Step 2: Create AWS Secrets

Create secrets in AWS Secrets Manager for your API keys:

```bash
# Create Gemini API key secret
aws secretsmanager create-secret \
  --name "911-call-generator/gemini-api-key" \
  --description "Google Gemini API key for 911 Call Generator" \
  --secret-string "YOUR_GEMINI_API_KEY"

# Create ElevenLabs API key secret
aws secretsmanager create-secret \
  --name "911-call-generator/elevenlabs-api-key" \
  --description "ElevenLabs API key for 911 Call Generator" \
  --secret-string "YOUR_ELEVENLABS_API_KEY"

# Get the ARNs (you'll need these for terraform.tfvars)
aws secretsmanager describe-secret --secret-id "911-call-generator/gemini-api-key" --query 'ARN' --output text
aws secretsmanager describe-secret --secret-id "911-call-generator/elevenlabs-api-key" --query 'ARN' --output text
```

### Step 3: Build and Push Docker Image

```bash
# Run the build and push script
./build-and-push.sh

# Follow the prompts (press Enter to use defaults)
# The script will:
# 1. Build the Docker image for linux/amd64
# 2. Create ECR repository if it doesn't exist
# 3. Authenticate with ECR
# 4. Push the image to ECR
```

### Step 4: Configure Terraform

```bash
cd terraform

# Copy the example tfvars file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

Required values to update in `terraform.tfvars`:
- `vpc_id`: Your VPC ID
- `private_subnet_ids`: List of private subnet IDs
- `gemini_api_key_secret_arn`: ARN from Step 2
- `elevenlabs_api_key_secret_arn`: ARN from Step 2

Optional values:
- `domain_zone` and `domain_subdomain` for custom domain
- `cpu` and `memory` for resource sizing
- `min_instances` and `max_instances` for scaling

### Step 5: Initialize Terraform

```bash
terraform init
```

This will download the AWS provider and initialize the backend.

### Step 6: Review the Plan

```bash
terraform plan
```

Review the resources that will be created:
- App Runner service
- App Runner service role
- VPC connector with security groups
- VPC endpoint
- Auto-scaling configuration
- IAM roles and policies
- Route53 records (if custom domain configured)

### Step 7: Deploy

```bash
terraform apply
```

Type `yes` when prompted. The deployment typically takes 5-10 minutes.

### Step 8: Verify Deployment

After successful deployment, Terraform will output:
```
Outputs:

service_url = "https://xxxxxxxxx.us-east-1.awsapprunner.com"
service_status = "RUNNING"
custom_domain = {
  domain = "your-subdomain.your-domain.com"
  status = "Check Route53 for DNS validation records"
}
```

Test the service:
```bash
# Health check
curl https://your-service-url/health

# Access the web interface
open https://your-service-url
```

## Updating the Application

### Update Code and Redeploy

1. **Make code changes** in your local repository

2. **Build and push new image**:
   ```bash
   ./build-and-push.sh
   # Use a new tag (e.g., v1.1.0) or latest
   ```

3. **Update Terraform** (if using versioned tags):
   ```bash
   cd terraform
   # Edit terraform.tfvars and update image_tag
   terraform apply
   ```

4. **Automatic deployment**: If using `latest` tag and auto-deployments are enabled, App Runner will automatically detect and deploy the new image.

### Update Infrastructure

```bash
cd terraform

# Edit terraform.tfvars with new values
nano terraform.tfvars

# Apply changes
terraform plan
terraform apply
```

## Monitoring and Logs

### View Logs

```bash
# Get service ARN from Terraform output
terraform output service_arn

# View logs in CloudWatch
aws logs tail "/aws/apprunner/YOUR-SERVICE-NAME/YOUR-SERVICE-ID/application" --follow
```

### Monitor Service

- **AWS Console**: Go to App Runner → Services → YOUR-SERVICE-NAME
- **CloudWatch Metrics**: CPU, Memory, Request count, Response time
- **CloudWatch Logs**: Application logs and system logs

## Troubleshooting

### Common Issues

1. **Service won't start**
   - Check CloudWatch logs for application errors
   - Verify secrets are accessible (IAM permissions)
   - Ensure ffmpeg is installed in Docker image

2. **Health check failing**
   - Verify `/health` endpoint is accessible
   - Check if app is binding to correct port (8080)
   - Review health check timeout settings

3. **Can't access external APIs**
   - Ensure NAT Gateway is configured in VPC
   - Check VPC connector security group rules
   - Verify egress rules allow HTTPS (443)

4. **Image push fails**
   - Authenticate with ECR: `aws ecr get-login-password | docker login...`
   - Check IAM permissions for ECR
   - Verify Docker is running

5. **Terraform errors**
   - Check jagger module path is correct
   - Ensure AWS credentials are configured
   - Verify required variables are set in terraform.tfvars

### Debug Mode

To enable debug logging:

1. Update `terraform/main.tf`:
   ```hcl
   env_vars = {
     LOG_LEVEL = "DEBUG"
   }
   ```

2. Apply changes:
   ```bash
   cd terraform
   terraform apply
   ```

## Cost Estimation

Approximate monthly costs (us-east-1):
- App Runner (1 vCPU, 2GB, running 24/7): ~$35-50/month
- ECR (image storage): ~$1/month
- VPC Connector: ~$7/month
- Data transfer: Variable based on usage
- **Total**: ~$45-60/month base cost

Scaling will increase costs proportionally.

## Security Considerations

1. **API Keys**: Never commit secrets to git. Always use AWS Secrets Manager.
2. **VPC**: Service is private-only, not publicly accessible
3. **IAM**: Follow least-privilege principle for service roles
4. **Encryption**: Secrets are encrypted at rest with AWS KMS
5. **HTTPS**: All traffic is encrypted in transit

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

Type `yes` when prompted. This will delete:
- App Runner service
- VPC connector and endpoint
- IAM roles
- Route53 records

Note: ECR repository and Secrets Manager secrets are preserved and must be deleted manually if desired:

```bash
# Delete ECR repository
aws ecr delete-repository --repository-name 911-call-generator --force

# Delete secrets
aws secretsmanager delete-secret --secret-id "911-call-generator/gemini-api-key" --force-delete-without-recovery
aws secretsmanager delete-secret --secret-id "911-call-generator/elevenlabs-api-key" --force-delete-without-recovery
```

## Additional Resources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [Google Gemini API Documentation](https://ai.google.dev/docs)

## Support

For issues or questions:
1. Check CloudWatch logs first
2. Review this deployment guide
3. Consult the [README.md](./README.md) for application details
4. Check the [PROJECT_NOTES.md](./PROJECT_NOTES.md) for architecture decisions

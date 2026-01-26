#!/bin/bash
# Build and push 911-call-generator Docker image to ECR
#
# The script will prompt you for ECR registry, image name, and tag.
# Press Enter to use the default values shown in brackets.

set -euo pipefail

# Default values - update these for your environment
DEFAULT_IMAGE_NAME="911-call-generator"
DEFAULT_IMAGE_TAG="latest"
DEFAULT_AWS_REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Get AWS Account ID for ECR registry
log "Getting AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [[ -z "${AWS_ACCOUNT_ID}" ]]; then
    error "Could not determine AWS Account ID. Please ensure AWS credentials are configured."
fi

DEFAULT_ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${DEFAULT_AWS_REGION}.amazonaws.com"

# Prompt for input
read -p "ECR Registry [${DEFAULT_ECR_REGISTRY}]: " ECR_REGISTRY
ECR_REGISTRY="${ECR_REGISTRY:-${DEFAULT_ECR_REGISTRY}}"

read -p "Image Name [${DEFAULT_IMAGE_NAME}]: " IMAGE_NAME
IMAGE_NAME="${IMAGE_NAME:-${DEFAULT_IMAGE_NAME}}"

read -p "Image Tag [${DEFAULT_IMAGE_TAG}]: " IMAGE_TAG
IMAGE_TAG="${IMAGE_TAG:-${DEFAULT_IMAGE_TAG}}"

read -p "AWS Region [${DEFAULT_AWS_REGION}]: " AWS_REGION
AWS_REGION="${AWS_REGION:-${DEFAULT_AWS_REGION}}"

FULL_IMAGE="${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
log "Configuration:"
echo "  ECR Registry: ${ECR_REGISTRY}"
echo "  Image Name:   ${IMAGE_NAME}"
echo "  Image Tag:    ${IMAGE_TAG}"
echo "  Full Image:   ${FULL_IMAGE}"
echo "  AWS Region:   ${AWS_REGION}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Check for required tools
if ! command -v docker &> /dev/null; then
    error "Docker is required but not installed. Install from: https://docs.docker.com/get-docker/"
fi

if ! command -v aws &> /dev/null; then
    error "AWS CLI is required but not installed. Install from: https://aws.amazon.com/cli/"
fi

# Verify AWS credentials
log "Verifying AWS credentials..."
if ! aws sts get-caller-identity --region "${AWS_REGION}" &> /dev/null; then
    error "AWS credentials are not configured or invalid. Please configure using:
  - aws configure
  - aws sso login
  - Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
fi

# Check if ECR repository exists
log "Checking if ECR repository exists: ${IMAGE_NAME}"
if ! aws ecr describe-repositories --repository-names "${IMAGE_NAME}" --region "${AWS_REGION}" &> /dev/null; then
    warn "ECR repository '${IMAGE_NAME}' does not exist. Creating it now..."
    aws ecr create-repository \
        --repository-name "${IMAGE_NAME}" \
        --region "${AWS_REGION}" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    log "ECR repository created successfully"
fi

# Authenticate Docker to ECR
log "Authenticating Docker to ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | \
    docker login --username AWS --password-stdin "${ECR_REGISTRY}"

if [[ $? -ne 0 ]]; then
    error "Failed to authenticate Docker with ECR"
fi

# Build Docker image
log "Building Docker image: ${FULL_IMAGE}"
log "Building for linux/amd64 platform (App Runner requirement)..."
docker buildx build --platform=linux/amd64 -t "${FULL_IMAGE}" .

if [[ $? -ne 0 ]]; then
    error "Docker build failed"
fi

log "Docker build completed successfully"

# Push to ECR
log "Pushing image to ECR: ${FULL_IMAGE}"
docker push "${FULL_IMAGE}"

if [[ $? -ne 0 ]]; then
    error "Docker push failed. Check:
  - ECR repository permissions
  - Network connectivity
  - Docker daemon is running"
fi

echo ""
log "✅ Image successfully pushed to ECR!"
echo ""
log "Next steps:"
echo "  1. Update terraform/terraform.tfvars with image tag: ${IMAGE_TAG}"
echo "  2. Run: cd terraform && terraform apply"
echo "  3. App Runner will automatically deploy the new image"
echo ""

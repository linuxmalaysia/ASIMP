# OpenTofu integration test configuration for ALB HTTP Ingress Restrictions
# Verification check: Port 80 (HTTP) must be strictly isolated to the VPC CIDR block of 10.0.0.0/16.

run "verify_alb_http_ingress" {
  command = plan

  assert {
    condition     = var.http_ingress_cidr_blocks == ["10.0.0.0/16"]
    error_message = "ALB Port 80 HTTP ingress must be strictly isolated to the internal VPC CIDR block 10.0.0.0/16."
  }
}

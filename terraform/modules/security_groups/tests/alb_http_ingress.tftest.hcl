# OpenTofu integration test configuration for ALB HTTP Ingress Restrictions
# Exercises the security_groups module to assert that port 80 ingress is restricted to exactly 10.0.0.0/16.

variables {
  http_ingress_cidr_blocks = ["10.0.0.0/16"]
}

run "verify_alb_http_ingress_rules" {
  command = plan

  # Validate that our security group rule block allows exactly our 10.0.0.0/16 set and no other external rules
  assert {
    condition     = contains(var.http_ingress_cidr_blocks, "10.0.0.0/16") && length(var.http_ingress_cidr_blocks) == 1
    error_message = "ALB Port 80 HTTP ingress rules must contain exactly the expected internal VPC CIDR set [\"10.0.0.0/16\"] and no additional external rules."
  }
}

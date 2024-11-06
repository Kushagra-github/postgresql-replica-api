resource "aws_ssm_parameter" "replication_password" {
  name  = "/postgresql/replication_password"
  type  = "SecureString"
  value = random_password.replication_password.result
}

resource "aws_ssm_parameter" "primary_private_ip" {
  name  = "/postgresql/private_ip"
  type  = "SecureString"
  value = aws_instance.postgres_primary.private_ip
}
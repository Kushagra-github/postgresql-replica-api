output "primary_private_ip" {
  value = aws_instance.postgres_primary.private_ip
  description = "The private IP of the primary PostgreSQL instance"
}

output "primary_public_ip" {
  value = aws_instance.postgres_primary.public_ip
  description = "The public IP of the primary PostgreSQL instance"
}
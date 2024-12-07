output "primary_private_ip" {
  value = aws_instance.postgres_primary.private_ip
  description = "The private IP of the primary PostgreSQL instance"
}

output "primary_public_ip" {
  value = aws_instance.postgres_primary.public_ip
  description = "The public IP of the primary PostgreSQL instance"
}

output "replica_public_ips" {
  value = [for replica in aws_instance.postgres_replica : replica.public_ip]
  description = "The public IP of the replica PostgreSQL instance"
}

output "private_key" {
  value     = tls_private_key.generated_key.private_key_pem
  sensitive = true
}

resource "aws_instance" "postgres_primary" {
  ami           = "ami-0dee22c13ea7a9a67"
  instance_type = var.instance_type
  key_name      = aws_key_pair.generated_key_pair.key_name

  tags = { Name = "postgres-primary" }
}

resource "aws_instance" "postgres_replica" {
  count         = var.num_replicas
  ami           = "ami-0dee22c13ea7a9a67"
  instance_type = var.instance_type
  key_name      = aws_key_pair.generated_key_pair.key_name

  tags = { Name = "postgres-replica-${count.index + 1}" }
}

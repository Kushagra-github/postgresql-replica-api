# Generate a new SSH key pair
resource "tls_private_key" "generated_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create EC2 Key Pair from the generated private key
resource "aws_key_pair" "generated_key_pair" {
  key_name   = "generated-key"
  public_key = tls_private_key.generated_key.public_key_openssh
}

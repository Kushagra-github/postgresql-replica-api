resource "random_password" "replication_password" {
  length  = 16
  special = true
}

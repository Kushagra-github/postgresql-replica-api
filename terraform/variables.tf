
variable "postgres_version" { 
    default = "14" 
    }

variable "instance_type" { 
    default = "t2.micro" 
    }

variable "num_replicas" { 
    default = 2 
    }

variable "max_connections" { 
    default = 100 
    }

variable "shared_buffers" { 
    default = "256MB" 
    }
       
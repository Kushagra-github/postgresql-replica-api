# PostgreSQL Replica API
This project sets up a PostgreSQL database with replication using FastAPI for API endpoints, Terraform for infrastructure provisioning on AWS, and Ansible for PostgreSQL configuration.

## Project Structure
```bash
postgresql-replica-api/
├── main.py               # FastAPI app
├── requirements.txt      # Python dependencies
├── terraform/
│   ├── main.tf           # Terraform file for EC2 and networking
│   ├── variables.tf      # Terraform variable definitions
│   ├── ssm.tf            # Terraform file for AWS Systems Manager parameters (e.g., storing secrets)
│   ├── password.tf       # Terraform file for generating secure passwords
│   ├── outputs.tf        # Terraform outputs for IP addresses
│   └── provider.tf       # Terraform provider configurations
└── ansible/
    ├── playbook.yml      # Ansible playbook to configure PostgreSQL
    └── roles/
        └── postgresql/
            ├── tasks/
                ├── install.yml      # Installation tasks
                └── replication.yml  # Replication tasks
            └── templates/
                ├── postgresql.conf.j2    # PostgreSQL config template
                └── pg_hba.conf.j2        # PostgreSQL host-based auth config
```

## Prerequisites
**Python 3.8+:** Install from Python's official website.   
**Terraform:** Install from Terraform's official website.   
**Ansible:** Install via `pip install ansible`.    
**AWS CLI:** For configuring AWS credentials.  

## Setup Guide
### Clone the repository:

```bash
git clone https://github.com/Kushagra-github/postgresql-replica-api.git
cd postgresql-replica-api
```

### Install Python dependencies:

```bash
pip install -r requirements.txt
```
The above command will install the `FastAPI`, `uvicorn`, and `subprocess.run` dependencies.  
If any of the above dependecies does not install properly, then try installing them seperately.   

### Configure AWS CLI:
Configure your AWS by running `aws configure` command. Ensure that AWS credentials are properly set up in `~/.aws/credentials`.

# Usage
## FastAPI Endpoints
### 1. Run the FastAPI server
In the root directory, start the FastAPI app:

```bash
uvicorn main:app --reload
```

### 2. Available Endpoints    
Open another terminal to run the following endpoints.

| Endpoint   | Description                          | Method |
|------------|--------------------------------------|--------|
| `/generate` | Generates infrastructure with specified parameters  | POST   |
| `/init`    | Initializes Terraform                | POST   |
| `/plan`    | Generates and shows execution plan   | POST   |
| `/apply`   | Applies the Terraform configuration  | POST   |
| `/destroy` | Destroys the Terraform-managed infrastructure | POST   |

### Example curl requests
**- Generate Configuration:**
Pass the parameters here to generate the configuration.

```bash
curl -X POST "http://127.0.0.1:8000/generate" -H "Content-Type: application/json" -d '{
    "postgres_version": "14",
    "instance_type": "t2.micro",
    "num_replicas": 2,
    "max_connections": 100,
    "shared_buffers": "256MB"
}'
```

**- Initialize Terraform:** 
```bash
curl -X POST "http://127.0.0.1:8000/init"
```

**- Plan Infrastructure:**

```bash
curl -X POST "http://127.0.0.1:8000/plan"
```

**- Apply Configuration:**

```bash
curl -X POST "http://127.0.0.1:8000/apply"
```

**- Destroy Infrastructure:**

```bash
curl -X POST "http://127.0.0.1:8000/destroy"
```

## Terraform Resources
This setup creates:

**EC2 Instances:** Primary and replica instances for PostgreSQL.   
**SSM Parameter Store:** Securely stores the replication password.

## Ansible Playbook
The Ansible playbook is used to install and configure PostgreSQL on the EC2 instances:

**Installation:** Installs PostgreSQL on both primary and replica nodes.   
**Replication:** Configures replication settings using `postgresql.conf.j2` and `pg_hba.conf.j2` templates.

# Cleanup
Make sure to destroy the deployed resources on AWS after the testing to avoid incurring any unwanted costs.   
```bash
curl -X POST "http://127.0.0.1:8000/destroy"
```
Run the above command to destroy the deployed resources.

from fastapi import FastAPI, HTTPException
import subprocess
from pydantic import BaseModel
import os
import json
import re

app = FastAPI()

# Path configurations
TERRAFORM_PATH = "./terraform"
ANSIBLE_PLAYBOOK = os.path.abspath("./ansible/playbook.yml")
INVENTORY_PATH = os.path.abspath("./ansible/inventory.ini")
PRIVATE_KEY_PATH = "./private_key.pem"


# Function to remove ANSI escape codes
def remove_ansi_escape_codes(text: str) -> str:
    ansi_escape = re.compile(r'\x1B\[[0-?9;]*[mK]')
    return ansi_escape.sub('', text)

# Pydantic model for the input parameters
class ConfigRequest(BaseModel):
    postgres_version: str
    instance_type: str
    num_replicas: int
    max_connections: int
    shared_buffers: str

def run_terraform():
    try:
        # Run terraform apply to provision resources
        print("Running terraform apply...")
        subprocess.run(["terraform", "apply", "-auto-approve"], check=True, cwd=TERRAFORM_PATH)
        
        # Fetch and save the private key
        private_key = subprocess.check_output(["terraform", "output", "private_key"], cwd=TERRAFORM_PATH).decode("utf-8").strip()
        print("Private Key:", private_key)  # Check if private key is returned

        if os.path.exists("private_key.pem"):
            os.remove("private_key.pem")
        with open("private_key.pem", "w") as key_file:
            key_file.write(private_key)
        
        os.chmod("private_key.pem", 0o400)
        
        # Fetch the primary and replica IPs using JSON parsing
        primary_ip = subprocess.check_output(["terraform", "output", "-json", "primary_public_ip"], cwd=TERRAFORM_PATH).decode("utf-8")
        primary_ip = json.loads(primary_ip) if primary_ip else None
        print("Primary IP:", primary_ip)

        replica_ips = subprocess.check_output(["terraform", "output", "-json", "replica_public_ips"], cwd=TERRAFORM_PATH).decode("utf-8")
        replica_ips = json.loads(replica_ips) if replica_ips else []
        print("Replica IPs:", replica_ips)
        
        # Generate the inventory.ini file for Ansible
        with open(INVENTORY_PATH, "w") as inventory_file:
            # Write the primary node to the inventory
            inventory_file.write(f"[primary]\n{primary_ip}\n")
            # Write the replica nodes to the inventory
            inventory_file.write(f"[replica]\n")
            for replica_ip in replica_ips:
                inventory_file.write(f"{replica_ip}\n")
        
        print(f"Inventory file created at {INVENTORY_PATH}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during terraform apply or fetching outputs: {e}")
        raise HTTPException(status_code=500, detail="Error running Terraform or retrieving IP addresses")


# Function to run Ansible playbook
def run_ansible():
    try:
        # Run the Ansible playbook with the private key
        process = subprocess.run(
            f"ansible-playbook -i {INVENTORY_PATH} {ANSIBLE_PLAYBOOK} --private-key {PRIVATE_KEY_PATH} -vvv",
            shell=True,
            cwd="./ansible",
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Ansible playbook error: {process.stderr}"
            )

        return {"message": "Ansible playbook executed successfully", "output": process.stdout}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running Ansible playbook: {str(e)}"
        )


# Endpoint to generate Terraform and Ansible configuration based on input parameters
@app.post("/generate")
async def generate_config(config: ConfigRequest):
    try:
        # Save parameters to Terraform variable file
        with open(f"{TERRAFORM_PATH}/variables.tf", "w") as tf_vars:
            tf_vars.write(f"""
            variable "postgres_version" {{ default = "{config.postgres_version}" }}
            variable "instance_type" {{ default = "{config.instance_type}" }}
            variable "num_replicas" {{ default = {config.num_replicas} }}
            variable "max_connections" {{ default = {config.max_connections} }}
            variable "shared_buffers" {{ default = "{config.shared_buffers}" }}
            """)

        return {"status": "Configuration generated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating configuration: {str(e)}")
    
# Endpoint to initialize Terraform
@app.post("/init")
async def terraform_init():
    try:
        # Set environment variable to disable color
        env = os.environ.copy()
        env["TF_NO_COLOR"] = "1"

        # Initialize Terraform
        result = subprocess.run(["terraform", "init"], cwd=TERRAFORM_PATH, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        # Clean the output and split it into lines
        cleaned_output = remove_ansi_escape_codes(result.stdout).strip().split('\n')

        return {
            "status": "Terraform initialized successfully.",
            "output": cleaned_output  # Return as a list of strings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to run terraform plan
@app.post("/plan")
async def terraform_plan():
    try:
        # Set environment variable to disable color
        env = os.environ.copy()
        env["TF_NO_COLOR"] = "1"

        # Run terraform plan
        result = subprocess.run(["terraform", "plan"], cwd=TERRAFORM_PATH, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        # Clean the output and split it into lines
        cleaned_output = remove_ansi_escape_codes(result.stdout).strip().split('\n')

        return {
            "status": "Terraform plan executed successfully.",
            "output": cleaned_output  # Return as a list of strings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run Terraform apply and generate inventory file for ansible
# @app.post("/apply")
# async def terraform_apply():
#     """
#     Run 'terraform apply' to create the infrastructure and generate Ansible inventory.
#     """
#     try:
#         # Run Terraform apply
#         process = subprocess.run(["terraform", "apply", "-auto-approve"], cwd=TERRAFORM_PATH, capture_output=True, text=True)
#         if process.returncode != 0:
#             raise HTTPException(status_code=500, detail=f"Terraform apply error: {process.stderr}")
        
#         # Get Terraform output in JSON format
#         output_process = subprocess.run(["terraform", "output", "-json"], cwd=TERRAFORM_PATH, capture_output=True, text=True)
#         terraform_output = json.loads(output_process.stdout)
        
#         # Write Ansible inventory file
#         with open("./ansible/inventory.ini", "w") as inventory_file:
#             primary_ip = terraform_output["primary_public_ip"]["value"]
#             replica_ips = terraform_output["replica_public_ips"]["value"]
            
#             inventory_file.write("[primary]\n")
#             inventory_file.write(f"{primary_ip}\n\n")
#             inventory_file.write("[replicas]\n")
#             for ip in replica_ips:
#                 inventory_file.write(f"{ip}\n")
        
#         return {"message": "Terraform apply executed successfully and inventory created", "output": process.stdout}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error running terraform apply or generating inventory: {str(e)}")
    
# # Run ansible playbook
# @app.post("/configure")
# async def configure_postgresql():
#     """
#     Run the Ansible playbook to install and configure PostgreSQL with replication.
#     """
#     try:
#         process = subprocess.run(
#             ["ansible-playbook", ANSIBLE_PLAYBOOK, "-i", "./ansible/inventory.ini"],
#             capture_output=True, text=True
#         )
#         if process.returncode != 0:
#             raise HTTPException(status_code=500, detail=f"Ansible playbook error: {process.stderr}")
#         return {"message": "Ansible playbook executed successfully", "output": process.stdout}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error running Ansible playbook: {str(e)}")


@app.post("/apply")
async def apply_configuration():
    # Step 1: Run Terraform to provision infrastructure and generate SSH key
    run_terraform()
    
    # Step 2: Run Ansible to configure PostgreSQL
    run_ansible()
    
     # Step 3: Clean up private key file after use (only if it exists)
    if os.path.exists("private_key.pem"):
        os.remove("private_key.pem")
    
    return {"status": "success", "message": "Infrastructure created and configured successfully"}



# Endpoint to destroy the infrastructure
@app.post("/destroy")
async def terraform_destroy():
    try:
        # Set environment variable to disable color
        env = os.environ.copy()
        env["TF_NO_COLOR"] = "1"

        # Destroy Terraform-managed infrastructure
        result = subprocess.run(
            ["terraform", "destroy", "-auto-approve"],
            cwd=TERRAFORM_PATH,
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        return {"status": "Infrastructure destroyed successfully.", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

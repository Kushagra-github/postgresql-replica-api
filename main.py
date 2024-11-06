from fastapi import FastAPI, HTTPException
import subprocess
from pydantic import BaseModel
import os
import json
import re

app = FastAPI()

# Path configurations
TERRAFORM_PATH = "./terraform"
ANSIBLE_PLAYBOOK = "./ansible/playbook.yml"

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

# Endpoint to apply terraform and run ansible
@app.post("/apply")
async def terraform_apply():
    try:
        # Set environment variable to disable color
        env = os.environ.copy()
        env["TF_NO_COLOR"] = "1"

        # Run terraform apply with auto-approve
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=TERRAFORM_PATH,
            capture_output=True,
            text=True,
            env=env
        )

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr.strip())

        # Clean the output and split it into lines
        cleaned_output = remove_ansi_escape_codes(result.stdout).strip().split('\n')

        return {
            "status": "Terraform apply executed successfully.",
            "output": cleaned_output  # Return as a list of strings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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

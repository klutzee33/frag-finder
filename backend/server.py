from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import json
import yaml
import subprocess
import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import re
import requests
from urllib.parse import quote

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fragrance Discounter Search Engine", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Data models
class InventoryHost(BaseModel):
    name: str
    ip: str
    user: str = "root"
    equipment_type: str = "server"
    location: str = "datacenter"
    ssh_key_path: Optional[str] = None

class AnsibleTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    variables: Dict[str, Any] = {}
    playbook_content: str

class PlaybookExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: Optional[str] = None
    hosts: List[str]
    variables: Dict[str, Any] = {}
    dry_run: bool = False
    status: str = "pending"
    output: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExecutionRequest(BaseModel):
    template_id: Optional[str] = None
    custom_playbook: Optional[str] = None
    hosts: List[str]
    variables: Dict[str, Any] = {}
    dry_run: bool = False

# Storage paths
STORAGE_DIR = Path("/app/ansible_data")
TEMPLATES_DIR = STORAGE_DIR / "templates"
INVENTORY_DIR = STORAGE_DIR / "inventory"
LOGS_DIR = STORAGE_DIR / "logs"
SSH_DIR = STORAGE_DIR / "ssh_keys"

# Ensure directories exist
for dir_path in [STORAGE_DIR, TEMPLATES_DIR, INVENTORY_DIR, LOGS_DIR, SSH_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Initialize default templates
DEFAULT_TEMPLATES = [
    {
        "id": "web_server_setup",
        "name": "Apache Web Server Setup",
        "description": "Install and configure Apache web server with basic security",
        "category": "Web Services",
        "variables": {
            "server_name": "example.com",
            "document_root": "/var/www/html",
            "enable_ssl": False
        },
        "playbook_content": """---
- name: Apache Web Server Setup
  hosts: all
  become: yes
  vars:
    server_name: "{{ server_name | default('localhost') }}"
    document_root: "{{ document_root | default('/var/www/html') }}"
    enable_ssl: "{{ enable_ssl | default(false) }}"
  
  tasks:
    - name: Install Apache
      yum:
        name: httpd
        state: present
    
    - name: Start and enable Apache
      systemd:
        name: httpd
        state: started
        enabled: yes
    
    - name: Configure Apache virtual host
      template:
        content: |
          <VirtualHost *:80>
              ServerName {{ server_name }}
              DocumentRoot {{ document_root }}
              ErrorLog logs/{{ server_name }}_error.log
              CustomLog logs/{{ server_name }}_access.log combined
          </VirtualHost>
        dest: /etc/httpd/conf.d/{{ server_name }}.conf
      notify: restart apache
    
    - name: Open firewall for HTTP
      firewalld:
        service: http
        permanent: yes
        state: enabled
        immediate: yes
      ignore_errors: yes
    
    - name: Open firewall for HTTPS
      firewalld:
        service: https
        permanent: yes
        state: enabled
        immediate: yes
      when: enable_ssl
      ignore_errors: yes
  
  handlers:
    - name: restart apache
      systemd:
        name: httpd
        state: restarted
"""
    },
    {
        "id": "security_hardening",
        "name": "RHEL 8 Security Hardening",
        "description": "Basic security hardening for RHEL 8 systems",
        "category": "Security",
        "variables": {
            "disable_root_login": True,
            "install_fail2ban": True,
            "update_system": True
        },
        "playbook_content": """---
- name: RHEL 8 Security Hardening
  hosts: all
  become: yes
  vars:
    disable_root_login: "{{ disable_root_login | default(true) }}"
    install_fail2ban: "{{ install_fail2ban | default(true) }}"
    update_system: "{{ update_system | default(true) }}"
  
  tasks:
    - name: Update all packages
      yum:
        name: "*"
        state: latest
      when: update_system
    
    - name: Install EPEL repository
      yum:
        name: epel-release
        state: present
    
    - name: Install fail2ban
      yum:
        name: fail2ban
        state: present
      when: install_fail2ban
    
    - name: Configure fail2ban
      copy:
        content: |
          [DEFAULT]
          bantime = 600
          findtime = 600
          maxretry = 3
          
          [sshd]
          enabled = true
        dest: /etc/fail2ban/jail.local
      when: install_fail2ban
      notify: restart fail2ban
    
    - name: Disable root SSH login
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin'
        line: 'PermitRootLogin no'
      when: disable_root_login
      notify: restart sshd
    
    - name: Set strong SSH configuration
      blockinfile:
        path: /etc/ssh/sshd_config
        block: |
          Protocol 2
          PasswordAuthentication no
          PermitEmptyPasswords no
          X11Forwarding no
          MaxAuthTries 3
        marker: "# {mark} ANSIBLE SECURITY CONFIG"
      notify: restart sshd
    
    - name: Configure firewall
      firewalld:
        service: ssh
        permanent: yes
        state: enabled
        immediate: yes
      ignore_errors: yes
  
  handlers:
    - name: restart fail2ban
      systemd:
        name: fail2ban
        state: restarted
        enabled: yes
    
    - name: restart sshd
      systemd:
        name: sshd
        state: restarted
"""
    },
    {
        "id": "user_management",
        "name": "User Management",
        "description": "Create and manage system users with proper security",
        "category": "System Administration",
        "variables": {
            "username": "newuser",
            "create_sudo_user": False,
            "ssh_public_key": ""
        },
        "playbook_content": """---
- name: User Management
  hosts: all
  become: yes
  vars:
    username: "{{ username | default('newuser') }}"
    create_sudo_user: "{{ create_sudo_user | default(false) }}"
    ssh_public_key: "{{ ssh_public_key | default('') }}"
  
  tasks:
    - name: Create user
      user:
        name: "{{ username }}"
        shell: /bin/bash
        create_home: yes
        state: present
    
    - name: Add user to sudo group
      user:
        name: "{{ username }}"
        groups: wheel
        append: yes
      when: create_sudo_user
    
    - name: Create .ssh directory
      file:
        path: "/home/{{ username }}/.ssh"
        state: directory
        owner: "{{ username }}"
        group: "{{ username }}"
        mode: '0700'
      when: ssh_public_key != ""
    
    - name: Add SSH public key
      authorized_key:
        user: "{{ username }}"
        key: "{{ ssh_public_key }}"
        state: present
      when: ssh_public_key != ""
    
    - name: Set password expiry
      shell: chage -M 90 {{ username }}
    
    - name: Create user home directory structure
      file:
        path: "/home/{{ username }}/{{ item }}"
        state: directory
        owner: "{{ username }}"
        group: "{{ username }}"
        mode: '0755'
      loop:
        - bin
        - scripts
        - logs
"""
    },
    {
        "id": "firewall_config",
        "name": "Firewall Configuration",
        "description": "Configure firewalld rules and security zones",
        "category": "Security",
        "variables": {
            "allowed_ports": ["22/tcp", "80/tcp", "443/tcp"],
            "default_zone": "public",
            "enable_logging": True
        },
        "playbook_content": """---
- name: Firewall Configuration
  hosts: all
  become: yes
  vars:
    allowed_ports: "{{ allowed_ports | default(['22/tcp', '80/tcp', '443/tcp']) }}"
    default_zone: "{{ default_zone | default('public') }}"
    enable_logging: "{{ enable_logging | default(true) }}"
  
  tasks:
    - name: Install firewalld
      yum:
        name: firewalld
        state: present
    
    - name: Start and enable firewalld
      systemd:
        name: firewalld
        state: started
        enabled: yes
    
    - name: Set default zone
      firewalld:
        zone: "{{ default_zone }}"
        state: enabled
        permanent: yes
        immediate: yes
    
    - name: Configure allowed ports
      firewalld:
        port: "{{ item }}"
        zone: "{{ default_zone }}"
        permanent: yes
        state: enabled
        immediate: yes
      loop: "{{ allowed_ports }}"
    
    - name: Enable firewall logging
      firewalld:
        zone: "{{ default_zone }}"
        permanent: yes
        state: enabled
        immediate: yes
      when: enable_logging
    
    - name: Remove unnecessary services
      firewalld:
        service: "{{ item }}"
        zone: "{{ default_zone }}"
        permanent: yes
        state: disabled
        immediate: yes
      loop:
        - dhcpv6-client
        - mdns
      ignore_errors: yes
    
    - name: Configure rich rules for SSH rate limiting
      firewalld:
        rich_rule: 'rule service name="ssh" accept limit value="3/m"'
        zone: "{{ default_zone }}"
        permanent: yes
        state: enabled
        immediate: yes
      ignore_errors: yes
"""
    }
]

def save_templates():
    """Save default templates to disk"""
    for template in DEFAULT_TEMPLATES:
        template_file = TEMPLATES_DIR / f"{template['id']}.json"
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2, default=str)

def load_templates():
    """Load all templates from disk"""
    templates = []
    for template_file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file, 'r') as f:
                template = json.load(f)
                templates.append(AnsibleTemplate(**template))
        except Exception as e:
            logger.error(f"Error loading template {template_file}: {e}")
    return templates

def check_ansible_version():
    """Check installed Ansible version and capabilities"""
    try:
        result = subprocess.run(['ansible', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_info = result.stdout.split('\n')[0]
            return {"installed": True, "version": version_info}
        else:
            return {"installed": False, "error": "Ansible not found"}
    except Exception as e:
        return {"installed": False, "error": str(e)}

def generate_inventory(hosts: List[InventoryHost]) -> str:
    """Generate Ansible inventory content"""
    inventory = {}
    
    for host in hosts:
        # Group by equipment type
        if host.equipment_type not in inventory:
            inventory[host.equipment_type] = {"hosts": {}}
        
        host_config = {
            "ansible_host": host.ip,
            "ansible_user": host.user
        }
        
        if host.ssh_key_path:
            host_config["ansible_ssh_private_key_file"] = host.ssh_key_path
        
        inventory[host.equipment_type]["hosts"][host.name] = host_config
    
    return yaml.dump(inventory, default_flow_style=False)

# Initialize templates on startup
save_templates()

# API Routes
@api_router.get("/ansible/version")
async def get_ansible_version():
    """Get Ansible version information"""
    return check_ansible_version()

@api_router.get("/templates", response_model=List[AnsibleTemplate])
async def get_templates():
    """Get all available templates"""
    return load_templates()

@api_router.post("/templates")
async def create_template(template: AnsibleTemplate):
    """Create a new custom template"""
    template_file = TEMPLATES_DIR / f"{template.id}.json"
    with open(template_file, 'w') as f:
        json.dump(template.dict(), f, indent=2, default=str)
    return {"message": "Template created successfully"}

@api_router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template"""
    template_file = TEMPLATES_DIR / f"{template_id}.json"
    if not template_file.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    
    with open(template_file, 'r') as f:
        template = json.load(f)
    return AnsibleTemplate(**template)

@api_router.get("/inventory")
async def get_inventory():
    """Get inventory hosts"""
    inventory_file = INVENTORY_DIR / "hosts.json"
    if not inventory_file.exists():
        return []
    
    with open(inventory_file, 'r') as f:
        hosts_data = json.load(f)
    return [InventoryHost(**host) for host in hosts_data]

@api_router.post("/inventory")
async def save_inventory(hosts: List[InventoryHost]):
    """Save inventory hosts"""
    inventory_file = INVENTORY_DIR / "hosts.json"
    hosts_data = [host.dict() for host in hosts]
    
    with open(inventory_file, 'w') as f:
        json.dump(hosts_data, f, indent=2)
    
    return {"message": "Inventory saved successfully"}

@api_router.post("/ssh/generate-key")
async def generate_ssh_key(key_name: str = "ansible_key"):
    """Generate SSH key pair"""
    try:
        key_path = SSH_DIR / key_name
        subprocess.run([
            'ssh-keygen', '-t', 'rsa', '-b', '4096', 
            '-f', str(key_path), '-N', '', '-q'
        ], check=True)
        
        # Read public key
        with open(f"{key_path}.pub", 'r') as f:
            public_key = f.read().strip()
        
        return {
            "private_key_path": str(key_path),
            "public_key_path": f"{key_path}.pub",
            "public_key_content": public_key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SSH key: {str(e)}")

@api_router.get("/ssh/keys")
async def list_ssh_keys():
    """List available SSH keys"""
    try:
        keys = []
        for key_file in SSH_DIR.glob("*.pub"):
            private_key = key_file.with_suffix('')
            if private_key.exists():
                with open(key_file, 'r') as f:
                    public_content = f.read().strip()
                keys.append({
                    "name": private_key.name,
                    "private_key_path": str(private_key),
                    "public_key_path": str(key_file),
                    "public_key_content": public_content
                })
        return keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list SSH keys: {str(e)}")

async def execute_playbook_stream(execution_id: str, playbook_content: str, inventory_content: str, variables: Dict[str, Any], dry_run: bool = False):
    """Execute Ansible playbook with streaming output"""
    try:
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write playbook
            playbook_file = temp_path / "playbook.yml"
            with open(playbook_file, 'w') as f:
                f.write(playbook_content)
            
            # Write inventory
            inventory_file = temp_path / "inventory.yml"
            with open(inventory_file, 'w') as f:
                f.write(inventory_content)
            
            # Write variables
            vars_file = temp_path / "vars.yml"
            with open(vars_file, 'w') as f:
                yaml.dump(variables, f)
            
            # Build command
            cmd = [
                'ansible-playbook',
                str(playbook_file),
                '-i', str(inventory_file),
                '-e', f'@{vars_file}',
                '-v'
            ]
            
            if dry_run:
                cmd.append('--check')
            
            # Execute
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            output_lines = []
            for line in process.stdout:
                output_lines.append(line)
                yield f"data: {json.dumps({'line': line, 'execution_id': execution_id})}\n\n"
            
            process.wait()
            
            # Save execution log
            log_file = LOGS_DIR / f"{execution_id}.log"
            with open(log_file, 'w') as f:
                f.writelines(output_lines)
            
            # Final status
            status = "completed" if process.returncode == 0 else "failed"
            yield f"data: {json.dumps({'status': status, 'execution_id': execution_id, 'return_code': process.returncode})}\n\n"
            
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e), 'execution_id': execution_id})}\n\n"

@api_router.post("/execute")
async def execute_playbook(request: ExecutionRequest, background_tasks: BackgroundTasks):
    """Execute Ansible playbook"""
    execution_id = str(uuid.uuid4())
    
    try:
        # Get playbook content
        if request.template_id:
            template_file = TEMPLATES_DIR / f"{request.template_id}.json"
            if not template_file.exists():
                raise HTTPException(status_code=404, detail="Template not found")
            
            with open(template_file, 'r') as f:
                template = json.load(f)
            playbook_content = template['playbook_content']
        elif request.custom_playbook:
            playbook_content = request.custom_playbook
        else:
            raise HTTPException(status_code=400, detail="Either template_id or custom_playbook must be provided")
        
        # Get inventory
        inventory_file = INVENTORY_DIR / "hosts.json"
        if not inventory_file.exists():
            raise HTTPException(status_code=400, detail="No inventory configured")
        
        with open(inventory_file, 'r') as f:
            hosts_data = json.load(f)
        
        # Filter requested hosts
        selected_hosts = [h for h in hosts_data if h['name'] in request.hosts]
        if not selected_hosts:
            raise HTTPException(status_code=400, detail="No valid hosts found")
        
        inventory_hosts = [InventoryHost(**h) for h in selected_hosts]
        inventory_content = generate_inventory(inventory_hosts)
        
        # Return streaming response
        return StreamingResponse(
            execute_playbook_stream(execution_id, playbook_content, inventory_content, request.variables, request.dry_run),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/executions")
async def get_execution_logs():
    """Get execution history"""
    logs = []
    for log_file in LOGS_DIR.glob("*.log"):
        execution_id = log_file.stem
        created_at = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        # Read first few lines to get context
        with open(log_file, 'r') as f:
            lines = f.readlines()
            preview = ''.join(lines[:5]) if lines else ""
        
        logs.append({
            "execution_id": execution_id,
            "created_at": created_at,
            "preview": preview,
            "log_file": str(log_file)
        })
    
    return sorted(logs, key=lambda x: x['created_at'], reverse=True)

@api_router.get("/executions/{execution_id}/log")
async def get_execution_log(execution_id: str):
    """Get full execution log"""
    log_file = LOGS_DIR / f"{execution_id}.log"
    if not log_file.exists():
        raise HTTPException(status_code=404, detail="Execution log not found")
    
    with open(log_file, 'r') as f:
        content = f.read()
    
    return {"execution_id": execution_id, "log_content": content}

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# RHEL 8 Ansible Script Writer & Executor - Local Deployment Guide

## Overview

This package provides a complete offline Ansible automation platform designed specifically for RHEL 8 systems. It includes a web-based interface for creating, managing, and executing Ansible playbooks with advanced features like inventory management, SSH key handling, and real-time execution monitoring.

## Features

- 🎯 **Template-Based Automation**: Pre-built templates for common RHEL 8 tasks
- 🔧 **Custom Playbook Editor**: Advanced YAML editor for custom automation
- 🖥️ **Inventory Management**: Organize hosts by equipment type and location
- 🔐 **SSH Key Management**: Automatic key generation and management
- ⚡ **Real-Time Execution**: Live output streaming during playbook execution
- 📊 **Execution Logging**: Complete history and log management
- 🌙 **Dark Mode Interface**: Professional, eye-friendly interface
- 🔒 **Security First**: Built-in security hardening and safe execution

## System Requirements

### Minimum Requirements
- **OS**: RHEL 8.x (or compatible)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 5GB free space
- **Network**: Internet access for initial setup (then runs offline)

### Software Dependencies (Auto-installed)
- Python 3.8+
- Node.js 16+
- Ansible 2.9+
- Git
- Development tools

## Quick Installation

### 1. Download and Extract
```bash
# Download the deployment package
wget https://your-repo/ansible-automation-platform.tar.gz
tar -xzf ansible-automation-platform.tar.gz
cd ansible-automation-platform
```

### 2. Run Installation Script
```bash
# Make installer executable
chmod +x deployment/install.sh

# Run as root
sudo ./deployment/install.sh
```

### 3. Access the Application
- Open your browser to: `http://localhost:3000`
- API available at: `http://localhost:8000`

## Manual Installation

If you prefer manual installation or need to customize the setup:

### 1. System Preparation
```bash
# Install EPEL repository
sudo dnf install -y epel-release

# Install system dependencies
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip nodejs npm git ansible
sudo npm install -g yarn
```

### 2. Create Application User
```bash
sudo useradd -r -s /bin/bash -m ansible-user
```

### 3. Create Directory Structure
```bash
sudo mkdir -p /opt/ansible-automation
sudo mkdir -p /var/lib/ansible-automation/{templates,inventory,logs,ssh_keys}
sudo mkdir -p /var/log/ansible-automation
sudo chown -R ansible-user:ansible-user /opt/ansible-automation /var/lib/ansible-automation /var/log/ansible-automation
```

### 4. Install Application
```bash
# Copy application files
sudo cp -r backend frontend /opt/ansible-automation/

# Install backend dependencies
cd /opt/ansible-automation/backend
sudo -u ansible-user python3 -m venv venv
sudo -u ansible-user ./venv/bin/pip install -r requirements.txt

# Install and build frontend
cd /opt/ansible-automation/frontend
sudo -u ansible-user yarn install
sudo -u ansible-user yarn build
```

### 5. Install SystemD Services
```bash
sudo cp deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ansible-automation-backend ansible-automation-frontend
sudo systemctl start ansible-automation-backend ansible-automation-frontend
```

## Configuration

### Environment Variables
Edit `/opt/ansible-automation/config/production.env` to customize:

- **BACKEND_PORT**: Backend API port (default: 8000)
- **FRONTEND_PORT**: Frontend port (default: 3000)
- **ANSIBLE_DATA_DIR**: Data storage location
- **LOG_LEVEL**: Logging verbosity

### Ansible Configuration
The installer creates `/etc/ansible/ansible.cfg` with optimized settings:

```ini
[defaults]
host_key_checking = False
retry_files_enabled = False
stdout_callback = yaml
log_path = /var/log/ansible-automation/ansible.log

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

### Firewall Configuration
If firewalld is enabled, the installer automatically opens required ports:
- Port 3000 (Frontend)
- Port 8000 (Backend API)

Manual firewall configuration:
```bash
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## Service Management

### SystemD Commands
```bash
# Start services
sudo systemctl start ansible-automation-backend ansible-automation-frontend

# Stop services  
sudo systemctl stop ansible-automation-backend ansible-automation-frontend

# Restart services
sudo systemctl restart ansible-automation-backend ansible-automation-frontend

# Check status
sudo systemctl status ansible-automation-backend
sudo systemctl status ansible-automation-frontend

# View logs
sudo journalctl -u ansible-automation-backend -f
sudo journalctl -u ansible-automation-frontend -f
```

### Application Logs
- **Application Logs**: `/var/log/ansible-automation/`
- **Ansible Execution Logs**: `/var/lib/ansible-automation/logs/`
- **SystemD Logs**: `journalctl -u ansible-automation-*`

## Usage Guide

### 1. Initial Setup
1. **Access Interface**: Open `http://localhost:3000`
2. **Generate SSH Keys**: Visit "SSH Keys" tab and generate your first key pair
3. **Add Inventory**: Go to "Inventory" tab and add your target hosts
4. **Verify Connectivity**: Test SSH connectivity to your hosts

### 2. Using Templates
1. **Browse Templates**: View pre-built templates in "Templates" tab
2. **Select Template**: Choose from Web Server, Security Hardening, User Management, or Firewall Configuration
3. **Customize Variables**: Modify template variables as needed
4. **Execute**: Run with dry-run mode first, then execute

### 3. Custom Playbooks
1. **Create Custom**: Click "Create Custom" in Templates tab
2. **Write YAML**: Use the built-in editor with syntax highlighting
3. **Save Template**: Save for reuse across multiple executions
4. **Execute**: Run your custom automation

### 4. Advanced Features
- **Inventory Grouping**: Organize hosts by equipment type and location
- **Execution History**: Review past executions and their outputs
- **Real-time Monitoring**: Watch live output during execution
- **Security Features**: Built-in SSH key management and secure execution

## Pre-built Templates

### 1. Apache Web Server Setup
- Installs and configures Apache HTTP Server
- Configures virtual hosts
- Sets up firewall rules
- Optional SSL/TLS configuration

### 2. RHEL 8 Security Hardening
- System updates and patches
- fail2ban installation and configuration
- SSH hardening (disable root login, key-only auth)
- Firewall configuration
- Security audit configurations

### 3. User Management
- Create system users with proper permissions
- Configure sudo access
- Set up SSH key authentication
- User directory structure creation
- Password policy enforcement

### 4. Firewall Configuration
- firewalld installation and configuration
- Security zone management
- Port and service rules
- Rich rule configuration
- Logging and monitoring setup

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check service status
sudo systemctl status ansible-automation-backend
sudo systemctl status ansible-automation-frontend

# Check logs
sudo journalctl -u ansible-automation-backend --since "10 minutes ago"
sudo journalctl -u ansible-automation-frontend --since "10 minutes ago"

# Verify file permissions
sudo chown -R ansible-user:ansible-user /opt/ansible-automation
```

#### Can't Access Web Interface
```bash
# Check if services are listening
sudo ss -tlun | grep -E "(3000|8000)"

# Check firewall
sudo firewall-cmd --list-ports

# Verify SELinux (if enabled)
sudo setsebool -P httpd_can_network_connect 1
```

#### Ansible Playbook Execution Fails
```bash
# Check Ansible installation
ansible --version

# Verify SSH connectivity
ssh -i /var/lib/ansible-automation/ssh_keys/ansible_key user@target-host

# Check Ansible logs
tail -f /var/log/ansible-automation/ansible.log
```

#### Permission Issues
```bash
# Fix ownership
sudo chown -R ansible-user:ansible-user /opt/ansible-automation /var/lib/ansible-automation

# Fix SSH key permissions
sudo chmod 600 /var/lib/ansible-automation/ssh_keys/*
sudo chmod 644 /var/lib/ansible-automation/ssh_keys/*.pub
```

### Log Files
- **Backend Logs**: `journalctl -u ansible-automation-backend`
- **Frontend Logs**: `journalctl -u ansible-automation-frontend`  
- **Ansible Logs**: `/var/log/ansible-automation/ansible.log`
- **Execution Logs**: `/var/lib/ansible-automation/logs/`

### Performance Tuning

#### For Large Inventories
Edit `/etc/ansible/ansible.cfg`:
```ini
[defaults]
forks = 50
timeout = 30

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
control_path_dir = /tmp/.ansible-cp
```

#### For High Frequency Execution
Increase system limits in `/etc/systemd/system/ansible-automation-backend.service`:
```ini
[Service]
LimitNOFILE=65536
LimitNPROC=32768
```

## Security Considerations

### Network Security
- Change default ports if exposed to public networks
- Use HTTPS proxy (nginx/Apache) for production deployments
- Implement VPN access for remote management

### SSH Key Security
- Regularly rotate SSH keys
- Use strong passphrases for key generation
- Limit SSH key access to specific hosts
- Monitor SSH key usage in logs

### Application Security
- Run services with minimal privileges
- Regular security updates
- Monitor execution logs for unusual activity
- Use SELinux in enforcing mode

## Backup and Recovery

### What to Backup
```bash
# Application data
/var/lib/ansible-automation/

# Configuration
/opt/ansible-automation/config/
/etc/ansible/ansible.cfg

# SSH keys
/var/lib/ansible-automation/ssh_keys/
```

### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backup/ansible-automation-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup application data
cp -r /var/lib/ansible-automation/ $BACKUP_DIR/data/
cp -r /opt/ansible-automation/config/ $BACKUP_DIR/config/
cp /etc/ansible/ansible.cfg $BACKUP_DIR/ansible.cfg

# Create archive
tar -czf $BACKUP_DIR.tar.gz -C /backup ansible-automation-$(date +%Y%m%d)
```

## Updating

### Update Application
```bash
# Stop services
sudo systemctl stop ansible-automation-backend ansible-automation-frontend

# Backup current installation
sudo cp -r /opt/ansible-automation /opt/ansible-automation.backup

# Update application files
sudo cp -r new-version/backend /opt/ansible-automation/
sudo cp -r new-version/frontend /opt/ansible-automation/

# Update dependencies
cd /opt/ansible-automation/backend
sudo -u ansible-user ./venv/bin/pip install -r requirements.txt

cd /opt/ansible-automation/frontend
sudo -u ansible-user yarn install
sudo -u ansible-user yarn build

# Start services
sudo systemctl start ansible-automation-backend ansible-automation-frontend
```

## Support and Resources

### Documentation
- Ansible Documentation: https://docs.ansible.com/
- RHEL 8 Documentation: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8

### Community Resources
- Ansible Galaxy: https://galaxy.ansible.com/
- Red Hat Customer Portal: https://access.redhat.com/

### Getting Help
1. Check application logs first
2. Review this documentation
3. Check Ansible and RHEL documentation
4. Contact your system administrator

## Uninstallation

### Complete Removal
```bash
# Stop and disable services
sudo systemctl stop ansible-automation-backend ansible-automation-frontend
sudo systemctl disable ansible-automation-backend ansible-automation-frontend

# Remove service files
sudo rm /etc/systemd/system/ansible-automation-*.service
sudo systemctl daemon-reload

# Remove application
sudo rm -rf /opt/ansible-automation
sudo rm -rf /var/lib/ansible-automation  
sudo rm -rf /var/log/ansible-automation

# Remove user (optional)
sudo userdel -r ansible-user

# Remove firewall rules (optional)
sudo firewall-cmd --permanent --remove-port=3000/tcp
sudo firewall-cmd --permanent --remove-port=8000/tcp
sudo firewall-cmd --reload
```

---

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Compatibility**: RHEL 8.x, CentOS 8, Rocky Linux 8, AlmaLinux 8
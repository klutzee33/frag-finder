#!/bin/bash

# RHEL 8 Ansible Script Writer & Executor - Local Installation Script
# Copyright (c) 2025 - Offline RHEL 8 Ansible Automation Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="ansible-automation"
APP_DIR="/opt/ansible-automation"
SERVICE_USER="ansible-user"
LOG_DIR="/var/log/ansible-automation"
DATA_DIR="/var/lib/ansible-automation"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

check_rhel8() {
    if ! grep -q "Red Hat Enterprise Linux" /etc/redhat-release 2>/dev/null; then
        print_warning "This script is designed for RHEL 8. Proceeding anyway..."
    fi
    
    if ! grep -q "release 8" /etc/redhat-release 2>/dev/null; then
        print_warning "This script is optimized for RHEL 8. Current version:"
        cat /etc/redhat-release
    fi
}

install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    # Enable EPEL repository
    dnf install -y epel-release
    
    # Install basic dependencies
    dnf groupinstall -y "Development Tools"
    dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        nodejs \
        npm \
        git \
        curl \
        wget \
        openssl \
        openssl-devel \
        libffi-devel \
        ansible \
        ansible-core \
        sshpass \
        rsync
    
    # Install yarn
    npm install -g yarn
    
    print_success "System dependencies installed successfully"
}

create_user() {
    print_status "Creating application user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/bash -m -d /home/$SERVICE_USER $SERVICE_USER
        print_success "User $SERVICE_USER created"
    else
        print_warning "User $SERVICE_USER already exists"
    fi
}

create_directories() {
    print_status "Creating application directories..."
    
    # Create main directories
    mkdir -p $APP_DIR
    mkdir -p $LOG_DIR
    mkdir -p $DATA_DIR
    mkdir -p $DATA_DIR/templates
    mkdir -p $DATA_DIR/inventory
    mkdir -p $DATA_DIR/logs
    mkdir -p $DATA_DIR/ssh_keys
    
    # Set ownership
    chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR
    chown -R $SERVICE_USER:$SERVICE_USER $LOG_DIR
    chown -R $SERVICE_USER:$SERVICE_USER $DATA_DIR
    
    # Set permissions
    chmod 755 $APP_DIR
    chmod 755 $LOG_DIR
    chmod 700 $DATA_DIR/ssh_keys
    
    print_success "Application directories created"
}

install_application() {
    print_status "Installing application files..."
    
    # Copy application files
    cp -r ./backend $APP_DIR/
    cp -r ./frontend $APP_DIR/
    cp -r ./deployment/systemd/* /etc/systemd/system/
    cp ./deployment/config/* $APP_DIR/
    
    # Create Python virtual environment
    cd $APP_DIR/backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    # Install frontend dependencies and build
    cd $APP_DIR/frontend
    yarn install
    yarn build
    
    # Set ownership
    chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR
    
    print_success "Application installed successfully"
}

configure_firewall() {
    print_status "Configuring firewall..."
    
    # Check if firewalld is running
    if systemctl is-active --quiet firewalld; then
        firewall-cmd --permanent --add-port=3000/tcp  # Frontend
        firewall-cmd --permanent --add-port=8000/tcp  # Backend
        firewall-cmd --reload
        print_success "Firewall configured"
    else
        print_warning "Firewalld is not running. Skipping firewall configuration."
    fi
}

configure_selinux() {
    print_status "Configuring SELinux..."
    
    if command -v setsebool &> /dev/null; then
        # Allow network connections
        setsebool -P httpd_can_network_connect 1
        setsebool -P httpd_can_network_connect_db 1
        
        # Set SELinux contexts
        semanage fcontext -a -t bin_t "$APP_DIR/backend/venv/bin(/.*)?" 2>/dev/null || true
        restorecon -R -v $APP_DIR 2>/dev/null || true
        
        print_success "SELinux configured"
    else
        print_warning "SELinux tools not available. Skipping SELinux configuration."
    fi
}

enable_services() {
    print_status "Enabling and starting services..."
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services
    systemctl enable ansible-automation-backend
    systemctl enable ansible-automation-frontend
    
    # Start services
    systemctl start ansible-automation-backend
    systemctl start ansible-automation-frontend
    
    print_success "Services enabled and started"
}

verify_installation() {
    print_status "Verifying installation..."
    
    sleep 5  # Give services time to start
    
    # Check service status
    if systemctl is-active --quiet ansible-automation-backend; then
        print_success "Backend service is running"
    else
        print_error "Backend service failed to start"
        systemctl status ansible-automation-backend
    fi
    
    if systemctl is-active --quiet ansible-automation-frontend; then
        print_success "Frontend service is running"
    else
        print_error "Frontend service failed to start"
        systemctl status ansible-automation-frontend
    fi
    
    # Check ports
    if ss -tlun | grep -q ":8000"; then
        print_success "Backend listening on port 8000"
    else
        print_warning "Backend not listening on port 8000"
    fi
    
    if ss -tlun | grep -q ":3000"; then
        print_success "Frontend listening on port 3000"
    else
        print_warning "Frontend not listening on port 3000"
    fi
}

create_ansible_config() {
    print_status "Creating Ansible configuration..."
    
    cat > /etc/ansible/ansible.cfg << 'EOF'
[defaults]
host_key_checking = False
retry_files_enabled = False
stdout_callback = yaml
bin_ansible_callbacks = True
log_path = /var/log/ansible-automation/ansible.log
private_key_file = /var/lib/ansible-automation/ssh_keys/ansible_key

[inventory]
enable_plugins = host_list, script, auto, yaml, ini, toml

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no
pipelining = True
EOF
    
    print_success "Ansible configuration created"
}

print_completion_info() {
    echo ""
    echo "================================================================"
    print_success "RHEL 8 Ansible Automation Platform Installation Complete!"
    echo "================================================================"
    echo ""
    echo -e "${BLUE}Access Information:${NC}"
    echo "  Frontend URL: http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo ""
    echo -e "${BLUE}Service Management:${NC}"
    echo "  Start:   systemctl start ansible-automation-backend ansible-automation-frontend"
    echo "  Stop:    systemctl stop ansible-automation-backend ansible-automation-frontend"
    echo "  Status:  systemctl status ansible-automation-backend ansible-automation-frontend"
    echo "  Logs:    journalctl -u ansible-automation-backend -f"
    echo "           journalctl -u ansible-automation-frontend -f"
    echo ""
    echo -e "${BLUE}File Locations:${NC}"
    echo "  Application: $APP_DIR"
    echo "  Data:        $DATA_DIR"
    echo "  Logs:        $LOG_DIR"
    echo "  Config:      /etc/ansible/ansible.cfg"
    echo ""
    echo -e "${BLUE}Initial Setup:${NC}"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Go to 'SSH Keys' tab and generate your first SSH key"
    echo "  3. Add hosts to your inventory"
    echo "  4. Start creating and executing Ansible playbooks!"
    echo ""
    echo -e "${YELLOW}Note: If you're accessing remotely, replace 'localhost' with your server's IP${NC}"
    echo ""
}

main() {
    print_status "Starting RHEL 8 Ansible Automation Platform installation..."
    
    check_root
    check_rhel8
    install_system_dependencies
    create_user
    create_directories
    install_application
    create_ansible_config
    configure_firewall
    configure_selinux
    enable_services
    verify_installation
    print_completion_info
}

# Check if we're being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
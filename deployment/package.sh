#!/bin/bash

# Package Creation Script for RHEL 8 Ansible Automation Platform
# Creates a complete deployment package for local installation

set -e

# Configuration
PACKAGE_NAME="ansible-automation-platform"
VERSION="1.0.0"
BUILD_DIR="build"
PACKAGE_DIR="$BUILD_DIR/$PACKAGE_NAME-$VERSION"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

create_package_structure() {
    print_status "Creating package structure..."
    
    # Clean and create build directory
    rm -rf $BUILD_DIR
    mkdir -p $PACKAGE_DIR
    
    # Create directory structure
    mkdir -p $PACKAGE_DIR/{backend,frontend,deployment/{systemd,config}}
    
    print_success "Package structure created"
}

copy_application_files() {
    print_status "Copying application files..."
    
    # Copy backend
    cp -r backend/* $PACKAGE_DIR/backend/
    
    # Copy frontend  
    cp -r frontend/* $PACKAGE_DIR/frontend/
    
    # Copy deployment files
    cp -r deployment/* $PACKAGE_DIR/deployment/
    
    # Copy root files
    cp README.md $PACKAGE_DIR/ 2>/dev/null || echo "# Ansible Automation Platform" > $PACKAGE_DIR/README.md
    
    print_success "Application files copied"
}

create_installer() {
    print_status "Creating installer script..."
    
    # Make install script executable
    chmod +x $PACKAGE_DIR/deployment/install.sh
    
    # Create main installer
    cat > $PACKAGE_DIR/install.sh << 'EOF'
#!/bin/bash

# RHEL 8 Ansible Automation Platform - Main Installer
# This script sets up the complete automation platform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "RHEL 8 Ansible Automation Platform Installer"
echo "Version: 1.0.0"
echo "=================================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "This installer must be run as root"
    echo "Please run: sudo ./install.sh"
    exit 1
fi

# Run the main installation script
cd "$SCRIPT_DIR"
./deployment/install.sh

echo ""
echo "Installation completed successfully!"
echo "You can now access the platform at: http://localhost:3000"
EOF

    chmod +x $PACKAGE_DIR/install.sh
    
    print_success "Installer script created"
}

create_quick_start() {
    print_status "Creating quick start guide..."
    
    cat > $PACKAGE_DIR/QUICKSTART.md << 'EOF'
# Quick Start Guide

## Installation (5 Minutes)

1. **Extract Package**
   ```bash
   tar -xzf ansible-automation-platform-1.0.0.tar.gz
   cd ansible-automation-platform-1.0.0
   ```

2. **Run Installer** (as root)
   ```bash
   sudo ./install.sh
   ```

3. **Access Application**
   - Open browser: http://localhost:3000
   - API endpoint: http://localhost:8000

## First Steps

1. **Generate SSH Keys**
   - Go to "SSH Keys" tab
   - Click "Generate New Key"

2. **Add Hosts**
   - Go to "Inventory" tab  
   - Add your RHEL 8 servers

3. **Run First Playbook**
   - Go to "Templates" tab
   - Select "Apache Web Server Setup"
   - Click "Use Template"
   - Select target hosts
   - Click "Execute Playbook"

## Service Management

```bash
# Start/Stop Services
sudo systemctl start ansible-automation-backend ansible-automation-frontend
sudo systemctl stop ansible-automation-backend ansible-automation-frontend

# View Logs
sudo journalctl -u ansible-automation-backend -f
sudo journalctl -u ansible-automation-frontend -f
```

## Files & Directories

- **Application**: `/opt/ansible-automation/`
- **Data**: `/var/lib/ansible-automation/`
- **Logs**: `/var/log/ansible-automation/`
- **Config**: `/etc/ansible/ansible.cfg`

## Support

For detailed documentation, see `README.md` or `/opt/ansible-automation/README.md` after installation.
EOF

    print_success "Quick start guide created"
}

create_version_info() {
    print_status "Creating version information..."
    
    cat > $PACKAGE_DIR/VERSION << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Build Date: $(date)
Target OS: RHEL 8.x
Architecture: x86_64

Components:
- Backend: FastAPI with Ansible integration
- Frontend: React with Tailwind CSS
- Templates: 4 pre-built automation templates
- Services: SystemD service definitions

Requirements:
- RHEL 8.x (or compatible)
- Python 3.8+
- Node.js 16+
- 2GB RAM minimum
- 5GB disk space
EOF

    print_success "Version information created"
}

create_archive() {
    print_status "Creating distribution archive..."
    
    cd $BUILD_DIR
    tar -czf $PACKAGE_NAME-$VERSION.tar.gz $PACKAGE_NAME-$VERSION/
    
    # Create checksum
    sha256sum $PACKAGE_NAME-$VERSION.tar.gz > $PACKAGE_NAME-$VERSION.tar.gz.sha256
    
    print_success "Archive created: $BUILD_DIR/$PACKAGE_NAME-$VERSION.tar.gz"
}

show_completion_info() {
    echo ""
    echo "================================================================"
    print_success "Package Creation Complete!"
    echo "================================================================"
    echo ""
    echo "Package: $BUILD_DIR/$PACKAGE_NAME-$VERSION.tar.gz"
    echo "Size: $(du -h $BUILD_DIR/$PACKAGE_NAME-$VERSION.tar.gz | cut -f1)"
    echo "SHA256: $(cat $BUILD_DIR/$PACKAGE_NAME-$VERSION.tar.gz.sha256 | cut -d' ' -f1)"
    echo ""
    echo "Distribution Instructions:"
    echo "1. Copy $PACKAGE_NAME-$VERSION.tar.gz to target RHEL 8 system"
    echo "2. Extract: tar -xzf $PACKAGE_NAME-$VERSION.tar.gz"  
    echo "3. Install: cd $PACKAGE_NAME-$VERSION && sudo ./install.sh"
    echo "4. Access: http://localhost:3000"
    echo ""
    echo "The package includes:"
    echo "✓ Complete application (backend + frontend)"
    echo "✓ SystemD service definitions"
    echo "✓ Automated installer script"
    echo "✓ Configuration templates"
    echo "✓ Comprehensive documentation"
    echo "✓ 4 pre-built Ansible templates"
    echo ""
}

main() {
    echo "Creating deployment package for RHEL 8 Ansible Automation Platform..."
    echo ""
    
    create_package_structure
    copy_application_files
    create_installer
    create_quick_start
    create_version_info
    create_archive
    show_completion_info
}

# Run main function
main "$@"
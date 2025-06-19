#!/bin/bash
# NCOS v21 Production Deployment Script
# Automated setup and deployment for NCOS v21 environment

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NCOS_VERSION="21.0"
DEPLOYMENT_DIR="./ncos_v21_deployment"
LOG_DIR="$DEPLOYMENT_DIR/logs"
DATA_DIR="$DEPLOYMENT_DIR/data"
CONFIG_DIR="$DEPLOYMENT_DIR/config"
STATE_DIR="$DEPLOYMENT_DIR/state"

echo -e "${GREEN}======================================"
echo "NCOS v21 Production Deployment Script"
echo "======================================${NC}"
echo "Version: $NCOS_VERSION"
echo "Deployment Directory: $DEPLOYMENT_DIR"
echo ""

# Function to check command availability
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        return 1
    fi
    return 0
}

# Function to create directory structure
create_directories() {
    echo -e "${YELLOW}Creating directory structure...${NC}"

    directories=(
        "$DEPLOYMENT_DIR"
        "$LOG_DIR"
        "$DATA_DIR"
        "$CONFIG_DIR"
        "$STATE_DIR"
        "$DEPLOYMENT_DIR/agents"
        "$DEPLOYMENT_DIR/tests"
        "$DEPLOYMENT_DIR/scripts"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo "  Created: $dir"
    done

    echo -e "${GREEN}✓ Directory structure created${NC}"
}

# Function to check Python dependencies
check_python_deps() {
    echo -e "${YELLOW}Checking Python environment...${NC}"

    # Check Python version
    if ! check_command python3; then
        echo -e "${RED}Python 3 is required but not installed${NC}"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "  Python version: $PYTHON_VERSION"

    # Check pip
    if ! check_command pip3; then
        echo -e "${RED}pip3 is required but not installed${NC}"
        exit 1
    fi

    # Create virtual environment if not exists
    if [ ! -d "$DEPLOYMENT_DIR/venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv "$DEPLOYMENT_DIR/venv"
    fi

    # Activate virtual environment
    source "$DEPLOYMENT_DIR/venv/bin/activate"

    echo -e "${GREEN}✓ Python environment ready${NC}"
}

# Function to install Python dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"

    # Create requirements.txt
    cat > "$DEPLOYMENT_DIR/requirements.txt" << EOF
pyyaml==6.0
pandas==2.0.3
numpy==1.24.3
pydantic==2.0.3
pyarrow==12.0.1
python-dateutil==2.8.2
EOF

    # Install dependencies
    pip install --upgrade pip
    pip install -r "$DEPLOYMENT_DIR/requirements.txt"

    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Function to extract deployment package
extract_package() {
    echo -e "${YELLOW}Extracting deployment package...${NC}"

    if [ ! -f "ncos_v21_production_candidate.tar.gz" ]; then
        echo -e "${RED}Error: ncos_v21_production_candidate.tar.gz not found${NC}"
        echo "Please ensure the deployment package is in the current directory"
        exit 1
    fi

    # Extract to deployment directory
    tar -xzf ncos_v21_production_candidate.tar.gz -C "$DEPLOYMENT_DIR"

    echo -e "${GREEN}✓ Package extracted${NC}"
}

# Function to setup configurations
setup_configurations() {
    echo -e "${YELLOW}Setting up configurations...${NC}"

    # Copy configuration files
    cp "$DEPLOYMENT_DIR"/config/*.yaml "$CONFIG_DIR/" 2>/dev/null || true

    # Create default bootstrap.yaml if not exists
    if [ ! -f "$CONFIG_DIR/bootstrap.yaml" ]; then
        cat > "$CONFIG_DIR/bootstrap.yaml" << EOF
version: '21.0'
system:
  name: 'NCOS'
  mode: 'production'
  single_session: true
initialization:
  parallel: false
  timeout: 300
  retry_attempts: 3
mesh:
  enable_broadcast: true
  heartbeat_interval: 60
logging:
  level: 'INFO'
  directory: '$LOG_DIR'
paths:
  data: '$DATA_DIR'
  state: '$STATE_DIR'
  config: '$CONFIG_DIR'
EOF
    fi

    echo -e "${GREEN}✓ Configurations ready${NC}"
}

# Function to verify agent files
verify_agents() {
    echo -e "${YELLOW}Verifying agent files...${NC}"

    required_agents=(
        "core_system_agent.py"
        "market_data_captain.py"
        "technical_analyst.py"
        "market_analyzer.py"
        "vector_memory_boot.py"
        "parquet_ingestor.py"
        "smc_router.py"
        "maz2_executor.py"
        "tmc_executor.py"
        "risk_guardian.py"
        "portfolio_manager.py"
        "broadcast_relay.py"
        "report_generator.py"
        "session_state_manager.py"
    )

    missing_agents=()

    for agent in "${required_agents[@]}"; do
        if [ ! -f "$DEPLOYMENT_DIR/agents/$agent" ]; then
            missing_agents+=("$agent")
        fi
    done

    if [ ${#missing_agents[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ All 13 agents verified${NC}"
    else
        echo -e "${RED}Missing agents:${NC}"
        for agent in "${missing_agents[@]}"; do
            echo "  - $agent"
        done
        echo -e "${YELLOW}Warning: Some agents are missing. System may not function properly.${NC}"
    fi
}

# Function to setup systemd service (optional)
setup_service() {
    echo -e "${YELLOW}Setting up NCOS service...${NC}"

    # Create service script
    cat > "$DEPLOYMENT_DIR/scripts/ncos_service.sh" << EOF
#!/bin/bash
# NCOS Service Script

cd "$DEPLOYMENT_DIR"
source venv/bin/activate
export PYTHONPATH="$DEPLOYMENT_DIR/agents:$PYTHONPATH"

# Start NCOS
python3 scripts/integration_bootstrap.py
EOF

    chmod +x "$DEPLOYMENT_DIR/scripts/ncos_service.sh"

    echo -e "${GREEN}✓ Service script created${NC}"
}

# Function to run initial tests
run_initial_tests() {
    echo -e "${YELLOW}Running initial system tests...${NC}"

    cd "$DEPLOYMENT_DIR"
    source venv/bin/activate
    export PYTHONPATH="$DEPLOYMENT_DIR/agents:$PYTHONPATH"

    # Run unit tests if available
    if [ -f "tests/test_ncos_agents.py" ]; then
        echo "  Running unit tests..."
        python3 -m unittest tests.test_ncos_agents -v 2>&1 | tee "$LOG_DIR/unit_tests.log"
    fi

    echo -e "${GREEN}✓ Initial tests completed${NC}"
}

# Function to create start/stop scripts
create_control_scripts() {
    echo -e "${YELLOW}Creating control scripts...${NC}"

    # Start script
    cat > "$DEPLOYMENT_DIR/start_ncos.sh" << EOF
#!/bin/bash
echo "Starting NCOS v21..."
cd "$DEPLOYMENT_DIR"
source venv/bin/activate
export PYTHONPATH="$DEPLOYMENT_DIR/agents:$PYTHONPATH"
nohup python3 scripts/integration_bootstrap.py > "$LOG_DIR/ncos.log" 2>&1 &
echo \$! > "$DEPLOYMENT_DIR/ncos.pid"
echo "NCOS started with PID: \$(cat $DEPLOYMENT_DIR/ncos.pid)"
EOF

    # Stop script
    cat > "$DEPLOYMENT_DIR/stop_ncos.sh" << EOF
#!/bin/bash
echo "Stopping NCOS v21..."
if [ -f "$DEPLOYMENT_DIR/ncos.pid" ]; then
    PID=\$(cat "$DEPLOYMENT_DIR/ncos.pid")
    if ps -p \$PID > /dev/null; then
        kill \$PID
        echo "NCOS stopped (PID: \$PID)"
    else
        echo "NCOS process not found"
    fi
    rm "$DEPLOYMENT_DIR/ncos.pid"
else
    echo "PID file not found"
fi
EOF

    # Status script
    cat > "$DEPLOYMENT_DIR/status_ncos.sh" << EOF
#!/bin/bash
if [ -f "$DEPLOYMENT_DIR/ncos.pid" ]; then
    PID=\$(cat "$DEPLOYMENT_DIR/ncos.pid")
    if ps -p \$PID > /dev/null; then
        echo "NCOS is running (PID: \$PID)"
        # Show recent logs
        echo ""
        echo "Recent logs:"
        tail -n 10 "$LOG_DIR/ncos.log"
    else
        echo "NCOS is not running (stale PID file)"
    fi
else
    echo "NCOS is not running"
fi
EOF

    chmod +x "$DEPLOYMENT_DIR"/*.sh

    echo -e "${GREEN}✓ Control scripts created${NC}"
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    echo ""

    # Step 1: Create directories
    create_directories
    echo ""

    # Step 2: Check Python environment
    check_python_deps
    echo ""

    # Step 3: Install dependencies
    install_dependencies
    echo ""

    # Step 4: Extract package
    extract_package
    echo ""

    # Step 5: Setup configurations
    setup_configurations
    echo ""

    # Step 6: Verify agents
    verify_agents
    echo ""

    # Step 7: Setup service
    setup_service
    echo ""

    # Step 8: Create control scripts
    create_control_scripts
    echo ""

    # Step 9: Run initial tests
    run_initial_tests
    echo ""

    # Deployment summary
    echo -e "${GREEN}======================================"
    echo "NCOS v21 Deployment Complete!"
    echo "======================================${NC}"
    echo ""
    echo "Deployment directory: $DEPLOYMENT_DIR"
    echo ""
    echo "Available commands:"
    echo "  ./start_ncos.sh   - Start NCOS system"
    echo "  ./stop_ncos.sh    - Stop NCOS system"
    echo "  ./status_ncos.sh  - Check NCOS status"
    echo ""
    echo "Logs directory: $LOG_DIR"
    echo "Configuration: $CONFIG_DIR/bootstrap.yaml"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review and adjust configurations in $CONFIG_DIR"
    echo "2. Start NCOS with ./start_ncos.sh"
    echo "3. Monitor logs in $LOG_DIR"
    echo ""
    echo -e "${GREEN}Deployment successful!${NC}"
}

# Run main deployment
main

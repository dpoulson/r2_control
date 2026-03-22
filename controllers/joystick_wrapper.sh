#!/bin/bash

# Configuration directories
BASE_DIR="/opt/r2_control"
CONT_DIR="$BASE_DIR/controllers"

# Read the currently active joystick
CURRENT=$(cat $CONT_DIR/.current 2>/dev/null || echo "ps3")

# Clean up any lingering shutdown flags
rm ~/.r2_config/.shutdown 2>/dev/null || true

echo "Joystick selected: $CURRENT"

# Switch into the joystick directory
cd "$CONT_DIR/$CURRENT" || exit 1

# Execute the controller script using the strict package virtual environment
$BASE_DIR/venv/bin/python3 "./r2_${CURRENT}.py"

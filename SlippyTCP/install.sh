#!/bin/sh

SLIPPYTCP_SERVICE_PATH="/etc/systemd/system/slippytcp.service"
SLIPPYTCP_SCRIPT_DIR="/usr/local/lib/slippytcp"
SLIPPYTCP_SCRIPT_PATH="$SLIPPYTCP_SCRIPT_DIR/slippytcp-server.py"

if [ ! -d $SLIPPYTCP_SCRIPT_DIR ]; then
	echo "Creating script installation directory"
	mkdir -p $SLIPPYTCP_SCRIPT_DIR
fi

echo "Installing python script"
cp ./slippytcp-server.py $SLIPPYTCP_SCRIPT_PATH
chown root:root $SLIPPYTCP_SCRIPT_PATH
chmod 644 $SLIPPYTCP_SCRIPT_PATH

echo "Installing systemd unit file"
cp ./slippytcp.service $SLIPPYTCP_SERVICE_PATH
chown root:root $SLIPPYTCP_SERVICE_PATH
chmod 644 $SLIPPYTCP_SERVICE_PATH

echo "Reloading systemd configuration"
systemctl daemon-reload

echo "Done"


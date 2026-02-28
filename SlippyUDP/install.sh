#!/bin/sh

SLIPPYUDP_SERVICE_PATH="/etc/systemd/system/slippyudp.service"
SLIPPYUDP_SCRIPT_DIR="/usr/local/lib/slippyudp"
SLIPPYUDP_SCRIPT_PATH="$SLIPPYUDP_SCRIPT_DIR/slippyudp.py"

echo "Installing systemd unit file"
cp ./slippyudp.service $SLIPPYUDP_SERVICE_PATH
chown root:root $SLIPPYUDP_SERVICE_PATH
chmod 644 $SLIPPYUDP_SERVICE_PATH

if [ ! -d $SLIPPYUDP_SCRIPT_DIR ]; then
	echo "Creating script installation directory"
	mkdir -p $SLIPPYUDP_SCRIPT_DIR
fi

echo "Installing python script"
cp ./slippyudp.py $SLIPPYUDP_SCRIPT_PATH
chown root:root $SLIPPYUDP_SCRIPT_PATH
chmod 644 $SLIPPYUDP_SCRIPT_PATH

echo "Reloading systemd configuration"
systemctl daemon-reload

echo "Done"

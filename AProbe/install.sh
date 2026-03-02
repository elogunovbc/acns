#!/bin/bash

###

# config
APROBE_SCRIPT_DIR="/usr/local/bin/aprobe"
APROBE_SCRIPT_PATH="${APROBE_SCRIPT_DIR}/aprobe.sh"
APROBE_SERVICE_NAME="aprobe.service"
APROBE_SERVICE_UNIT_PATH="/etc/systemd/system/${APROBE_SERVICE_NAME}"
APROBE_TIMER_NAME="aprobe.timer"
APROBE_TIMER_UNIT_PATH="/etc/systemd/system/${APROBE_TIMER_NAME}"

###

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root or using sudo" 1>&2
    exit 1
fi

###

if [ ! -d "${APROBE_SCRIPT_DIR}" ]; then
    echo "Creating script installation directory"
    mkdir -p "${APROBE_SCRIPT_DIR}"
fi

echo "Installing script"
cp ./aprobe.sh "${APROBE_SCRIPT_PATH}"
chown root:root "${APROBE_SCRIPT_PATH}"
chmod 744 "${APROBE_SCRIPT_PATH}"

###

echo "Installing systemd service unit"

cat << EOF > "${APROBE_SERVICE_UNIT_PATH}"
[Unit]
Description=Drop traffic from certain ASNs to protect from active probing
After=network-online.target

[Service]
Type=oneshot
Nice=19
ExecStart=${APROBE_SCRIPT_PATH}
EOF

chown root:root "${APROBE_SERVICE_UNIT_PATH}"
chmod 644 "${APROBE_SERVICE_UNIT_PATH}"

echo "Service installed: ${APROBE_SERVICE_NAME}"

###

echo "Installing systemd timer unit"

cat << EOF > "${APROBE_TIMER_UNIT_PATH}"
[Unit]
Description=Refresh prefixes of ASNs to drop traffic from
Wants=network-online.target

[Timer]
OnCalendar=daily
RandomizedDelaySec=60m
Persistent=true
Unit=${APROBE_SERVICE_NAME}

[Install]
WantedBy=timers.target
EOF

chown root:root "${APROBE_TIMER_UNIT_PATH}"
chmod 644 "${APROBE_TIMER_UNIT_PATH}"

echo "Timer installed: ${APROBE_TIMER_NAME}"

###

echo "Reloading systemd configuration"
systemctl daemon-reload

echo "Activating timer"
systemctl enable --now ${APROBE_TIMER_NAME}

echo "Done!"

###


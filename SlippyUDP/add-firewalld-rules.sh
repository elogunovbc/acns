#!/bin/sh

firewall-cmd --permanent --new-service=slippyudp
firewall-cmd --permanent --service=slippyudp --add-port=24540/udp
firewall-cmd --reload
firewall-cmd --permanent --info-service=slippyudp

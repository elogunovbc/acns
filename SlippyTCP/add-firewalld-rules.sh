#!/bin/sh

firewall-cmd --permanent --new-service=slippytcp
firewall-cmd --permanent --service=slippytcp --add-port=24154/tcp
firewall-cmd --permanent --service=slippytcp --add-port=24155/udp
firewall-cmd --reload
firewall-cmd --permanent --info-service=slippytcp


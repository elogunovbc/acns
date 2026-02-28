#!/bin/sh

firewall-cmd --permanent --delete-service=slippyudp
firewall-cmd --reload

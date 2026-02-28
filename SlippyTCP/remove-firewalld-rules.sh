#!/bin/sh

firewall-cmd --permanent --delete-service=slippytcp
firewall-cmd --reload


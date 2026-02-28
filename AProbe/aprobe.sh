#!/bin/bash

###

# config
ASNLIST=(AS196641 AS213853 AS61280)

###

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root or using sudo" 1>&2
    exit 1
fi

if ! command -v whois &> /dev/null; then
    echo "whois is not installed. You may need to install it (e.g. sudo dnf install whois)" 1>&2
    exit 1
fi

###

TMP_WHOISOUT=$(mktemp) || exit 1
TMP_NETCOLLAPSE=$(mktemp) || exit 1
TMP_OUTSCRIPT=$(mktemp) || exit 1

echo "TMP_WHOISOUT set to ${TMP_WHOISOUT}"
echo "TMP_NETCOLLAPSE set to ${TMP_NETCOLLAPSE}"
echo "TMP_OUTSCRIPT set to ${TMP_OUTSCRIPT}"

cleanup() {
    echo "Cleaning up temporary files..."
    rm -f "${TMP_WHOISOUT}"
    rm -f "${TMP_NETCOLLAPSE}"
    rm -f "${TMP_OUTSCRIPT}"
}

trap cleanup EXIT

###

for ASN in "${ASNLIST[@]}"; do
    echo "Querying RIPE db for ${ASN}..."
    whois -h whois.ripe.net -- "-K -i origin ${ASN}" >> "${TMP_WHOISOUT}" 2>&1
done

###

echo "Preparing python helper script..."

cat << EOF > "${TMP_NETCOLLAPSE}"
#!/usr/bin/python
import sys, ipaddress

lines = [line.strip() for line in sys.stdin]
nets = [ipaddress.ip_network(line) for line in lines if line]

for ip_ver in [4, 6]:
  collapsed = [net for net in nets if net.version == ip_ver]
  collapsed = sorted(ipaddress.collapse_addresses(collapsed))
  for net in collapsed:
    print(net.with_prefixlen)
EOF

chmod u+x "${TMP_NETCOLLAPSE}"

###

echo "Preparing output script..."

echo '#!/bin/bash' | tee "${TMP_OUTSCRIPT}"
firewall-cmd --zone=drop --list-sources | xargs -n 1 | xargs -I '$' echo 'firewall-cmd --permanent --zone=drop --remove-source=$' | tee -a "${TMP_OUTSCRIPT}"
grep '^route' "${TMP_WHOISOUT}" | uniq | awk '{ print $2; }' | "${TMP_NETCOLLAPSE}" | xargs -I '$' echo 'firewall-cmd --permanent --zone=drop --add-source=$' | tee -a "${TMP_OUTSCRIPT}"
echo 'firewall-cmd --reload' | tee -a "${TMP_OUTSCRIPT}"

chmod u+x "${TMP_OUTSCRIPT}"

###

echo "Executing output script..."

"${TMP_OUTSCRIPT}"

echo "Done!"

firewall-cmd --zone=drop --list-sources

###


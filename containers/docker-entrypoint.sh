#!/bin/bash
set -e

if [ -z "$BURP_PORT" ]; then
    echo "Error: BURP_PORT must be set."
    exit 1
fi

# Set default API port if not provided
export BURP_API_PORT=${BURP_API_PORT:-8090}

# Generate API key if not provided
if [ -z "$BURP_API_TOKEN" ]; then
    BURP_API_TOKEN=$(openssl rand -hex 32)
    echo "Generated BurpSuite Pro API key: $BURP_API_TOKEN"
fi

export BURP_API_TOKEN=$BURP_API_TOKEN

# Create BurpSuite Pro configuration directory
mkdir -p /home/pentester/.burpsuite

# Start BurpSuite Pro with REST API extension
echo "Starting BurpSuite Pro with REST API extension..."
echo "Proxy port: $BURP_PORT"
echo "API port: $BURP_API_PORT"
echo "API key: $BURP_API_TOKEN"

burpsuite-pro &

echo "Waiting for BurpSuite Pro REST API to be ready..."
for i in {1..60}; do
  if curl -s -o /dev/null http://localhost:${BURP_API_PORT}/v0.1/status; then
    echo "BurpSuite Pro REST API is ready."
    break
  fi
  sleep 2
done

if [ $i -eq 60 ]; then
  echo "Failed to start BurpSuite Pro REST API after 2 minutes."
  exit 1
fi

echo "✅ BurpSuite Pro with REST API started successfully."

echo "Configuring system-wide proxy settings..."

cat << EOF | sudo tee /etc/profile.d/proxy.sh
export http_proxy=http://127.0.0.1:${BURP_PORT}
export https_proxy=http://127.0.0.1:${BURP_PORT}
export HTTP_PROXY=http://127.0.0.1:${BURP_PORT}
export HTTPS_PROXY=http://127.0.0.1:${BURP_PORT}
export ALL_PROXY=http://127.0.0.1:${BURP_PORT}
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export BURP_API_TOKEN=${BURP_API_TOKEN}
export BURP_API_URL=http://localhost:${BURP_API_PORT}
EOF

cat << EOF | sudo tee /etc/environment
http_proxy=http://127.0.0.1:${BURP_PORT}
https_proxy=http://127.0.0.1:${BURP_PORT}
HTTP_PROXY=http://127.0.0.1:${BURP_PORT}
HTTPS_PROXY=http://127.0.0.1:${BURP_PORT}
ALL_PROXY=http://127.0.0.1:${BURP_PORT}
BURP_API_TOKEN=${BURP_API_TOKEN}
BURP_API_URL=http://localhost:${BURP_API_PORT}
EOF

cat << EOF | sudo tee /etc/wgetrc
use_proxy=yes
http_proxy=http://127.0.0.1:${BURP_PORT}
https_proxy=http://127.0.0.1:${BURP_PORT}
EOF

echo "source /etc/profile.d/proxy.sh" >> ~/.bashrc
echo "source /etc/profile.d/proxy.sh" >> ~/.zshrc

source /etc/profile.d/proxy.sh

echo "✅ System-wide proxy configuration complete"

echo "Adding CA to browser trust store..."
sudo -u pentester mkdir -p /home/pentester/.pki/nssdb
sudo -u pentester certutil -N -d sql:/home/pentester/.pki/nssdb --empty-password
sudo -u pentester certutil -A -n "Testing Root CA" -t "C,," -i /app/certs/ca.crt -d sql:/home/pentester/.pki/nssdb
echo "✅ CA added to browser trust store"

echo "Container initialization complete - agents will start their own tool servers as needed"
echo "✅ Shared container ready for multi-agent use"

cd /workspace

exec "$@"
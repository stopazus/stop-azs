#!/bin/bash
# Generate self-signed SSL certificates for local development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="${SCRIPT_DIR}/ssl"

# Create ssl directory if it doesn't exist
mkdir -p "${SSL_DIR}"

echo "Generating self-signed SSL certificate for local development..."

# Generate private key and certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "${SSL_DIR}/key.pem" \
    -out "${SSL_DIR}/cert.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=Development/CN=localhost"

echo "SSL certificates generated successfully!"
echo "Certificate: ${SSL_DIR}/cert.pem"
echo "Private key: ${SSL_DIR}/key.pem"
echo ""
echo "Note: These are self-signed certificates for local development only."
echo "Do not use in production!"

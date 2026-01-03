#!/bin/bash
# Simple test script for Zendesk MCP Server via Docker stdio
# This script sends basic MCP protocol messages to test the server

set -e

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Warning: $ENV_FILE not found. The server may fail without Zendesk credentials."
    echo "Create a .env file with:"
    echo "  ZENDESK_SUBDOMAIN=your-subdomain"
    echo "  ZENDESK_EMAIL=your-email@example.com"
    echo "  ZENDESK_API_KEY=your-api-token"
    echo ""
    echo "Continuing without env file..."
    ENV_ARGS=""
else
    ENV_ARGS="--env-file $ENV_FILE"
fi

echo "Testing Zendesk MCP Server via Docker stdio"
echo "============================================"
echo ""

# Build the Docker image if it doesn't exist
if ! docker image inspect zendesk-mcp-server >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t zendesk-mcp-server .
    echo ""
fi

# Create a temporary file with MCP protocol messages
TEMP_FILE=$(mktemp)
cat > "$TEMP_FILE" << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"prompts/list"}
{"jsonrpc":"2.0","id":4,"method":"resources/list"}
EOF

echo "Sending MCP protocol messages to the server..."
echo ""

# Run Docker container with stdin from the temp file
docker run --rm -i $ENV_ARGS zendesk-mcp-server < "$TEMP_FILE" | while IFS= read -r line; do
    echo "$line" | python3 -m json.tool 2>/dev/null || echo "$line"
done

# Clean up
rm -f "$TEMP_FILE"

echo ""
echo "Test completed!"


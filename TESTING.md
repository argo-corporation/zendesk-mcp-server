# Testing the Zendesk MCP Server with Docker

This guide explains how to test the Zendesk MCP server using Docker with stdio communication.

## Prerequisites

1. Docker installed and running
2. Zendesk credentials (subdomain, email, API token)
3. A `.env` file with your credentials (see below)

## Setup

### 1. Create Environment File

Create a `.env` file in the project root with your Zendesk credentials:

```bash
ZENDESK_SUBDOMAIN=your-subdomain
ZENDESK_EMAIL=your-email@example.com
ZENDESK_API_KEY=your-api-token
```

**Note:** The `.env` file should be kept private and not committed to version control.

### 2. Build Docker Image

```bash
docker build -t zendesk-mcp-server .
```

## Testing Methods

### Method 1: Python Test Script (Recommended)

The Python test script provides detailed output and proper MCP protocol handling:

```bash
python3 test_mcp_stdio.py
```

This script will:
- Check for `.env` file
- Start the Docker container
- Send initialization request
- List available tools, prompts, and resources
- Display formatted JSON responses

### Method 2: Shell Script

A simpler bash-based test:

```bash
./test_mcp_stdio.sh
```

Or with a custom env file:

```bash
./test_mcp_stdio.sh /path/to/custom.env
```

### Method 3: Manual Testing with Docker

You can manually test the server by sending MCP protocol messages:

```bash
# Create a test input file
cat > test_input.json << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
EOF

# Run with Docker
docker run --rm -i --env-file .env zendesk-mcp-server < test_input.json
```

### Method 4: Interactive Testing

For interactive testing, you can pipe commands:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \
docker run --rm -i --env-file .env zendesk-mcp-server
```

## Expected Output

When testing successfully, you should see:

1. **Initialization Response**: Server capabilities and version info
2. **Tools List**: Available Zendesk tools (get_ticket, create_ticket, etc.)
3. **Prompts List**: Available prompts (analyze-ticket, draft-ticket-response)
4. **Resources List**: Available resources (zendesk://knowledge-base)

## Testing Specific Tools

### Test Tool Listing

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | \
docker run --rm -i --env-file .env zendesk-mcp-server
```

### Test Getting a Ticket

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_ticket","arguments":{"ticket_id":1}}}' | \
docker run --rm -i --env-file .env zendesk-mcp-server
```

## Troubleshooting

### Docker Permission Issues

If you get permission errors, ensure:
- Docker daemon is running
- Your user is in the `docker` group (Linux)
- Docker Desktop is running (macOS/Windows)

### Missing Environment Variables

If the server fails to start, check:
- `.env` file exists and is readable
- All three required variables are set: `ZENDESK_SUBDOMAIN`, `ZENDESK_EMAIL`, `ZENDESK_API_KEY`
- No extra spaces or quotes around values in `.env`

### Connection Errors

If you see Zendesk API errors:
- Verify your credentials are correct
- Check your Zendesk subdomain is correct
- Ensure your API token has proper permissions
- Verify network connectivity to Zendesk

### JSON-RPC Errors

If you see protocol errors:
- Ensure each JSON message is on a single line
- Messages must be valid JSON
- Each request needs a unique `id` (except notifications)
- Follow the MCP protocol specification

## Integration with Claude Desktop

To use this Dockerized server with Claude Desktop, add to your `settings.json`:

```json
{
  "mcpServers": {
    "zendesk": {
      "command": "/usr/local/bin/docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/path/to/zendesk-mcp-server/.env",
        "zendesk-mcp-server"
      ]
    }
  }
}
```

**Note:** Adjust the Docker path and `.env` file path to match your system.


# Quick Test Guide

## Quick Start

1. **Create `.env` file** (if not exists):
   ```bash
   cat > .env << EOF
   ZENDESK_SUBDOMAIN=your-subdomain
   ZENDESK_EMAIL=your-email@example.com
   ZENDESK_API_KEY=your-api-token
   EOF
   ```

2. **Build Docker image**:
   ```bash
   docker build -t zendesk-mcp-server .
   ```

3. **Run test**:
   ```bash
   # Option 1: Python script (detailed output)
   python3 test_mcp_stdio.py
   
   # Option 2: Shell script (simple)
   ./test_mcp_stdio.sh
   
   # Option 3: Direct with test file
   docker run --rm -i --env-file .env zendesk-mcp-server < test_commands.jsonl
   ```

## What Gets Tested

- ✅ Server initialization
- ✅ Tools listing (get_ticket, create_ticket, etc.)
- ✅ Prompts listing (analyze-ticket, draft-ticket-response)
- ✅ Resources listing (knowledge-base)

## Expected Success Output

You should see JSON-RPC responses with:
- `"result"` objects containing tools, prompts, and resources
- No `"error"` objects
- Proper JSON formatting

For detailed information, see [TESTING.md](TESTING.md).


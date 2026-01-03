# Zendesk MCP Server

![ci](https://github.com/reminia/zendesk-mcp-server/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A Model Context Protocol server for Zendesk.

This server provides a comprehensive integration with Zendesk. It offers:

- Tools for retrieving and managing Zendesk tickets and comments
- Tools for listing and searching Zendesk users
- Specialized prompts for ticket analysis and response drafting
- Full access to the Zendesk Help Center articles as knowledge base

![demo](https://res.cloudinary.com/leecy-me/image/upload/v1736410626/open/zendesk_yunczu.gif)

## Setup

- build: `uv venv && uv pip install -e .` or `uv build` in short.
- setup zendesk credentials in `.env` file, refer to [.env.example](.env.example).
- configure in Claude desktop:

```json
{
  "mcpServers": {
      "zendesk": {
          "command": "uv",
          "args": [
              "--directory",
              "/path/to/zendesk-mcp-server",
              "run",
              "zendesk"
          ]
      }
  }
}
```

### Docker

You can containerize the server if you prefer an isolated runtime:

1. Copy `.env.example` to `.env` and fill in your Zendesk credentials. Keep this file outside version control.
2. Build the image:

   ```bash
   docker build -t zendesk-mcp-server .
   ```

3. Run the server, providing the environment file:

   ```bash
   docker run --rm --env-file /path/to/.env zendesk-mcp-server
   ```

   Add `-i` when wiring the container to MCP clients over STDIN/STDOUT (Claude Code uses this mode). For daemonized runs, add `-d --name zendesk-mcp`.

The image installs dependencies from `requirements.lock`, drops privileges to a non-root user, and expects configuration exclusively via environment variables.

#### Claude MCP Integration

To use the Dockerized server from Claude Code/Desktop, add an entry to Claude Code's `settings.json` similar to:

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

Adjust the paths to match your environment. After saving the file, restart Claude for the new MCP server to be detected.

## Resources

- zendesk://knowledge-base, get access to the whole help center articles.

## Prompts

### analyze-ticket

Analyze a Zendesk ticket and provide a detailed analysis of the ticket.

### draft-ticket-response

Draft a response to a Zendesk ticket.

## Tools

### get_tickets

Fetch tickets with pagination support. Supports filtering by organization, user, ticket type, or recent tickets.

- Input:
  - `page` (integer, optional): Page number (defaults to 1)
  - `per_page` (integer, optional): Number of tickets per page, max 100 (defaults to 25)
  - `sort_by` (string, optional): Field to sort by - created_at, updated_at, priority, or status (defaults to created_at)
  - `sort_order` (string, optional): Sort order - asc or desc (defaults to desc)
  - `organization_id` (integer, optional): Filter tickets by organization ID
  - `user_id` (integer, optional): Filter tickets by user ID (requires `ticket_type`)
  - `ticket_type` (string, optional): Type of tickets to fetch for a user - one of `requested`, `ccd`, `followed`, or `assigned` (requires `user_id`)
  - `recent` (boolean, optional): If true, fetch only tickets created or updated in the last 30 days (defaults to false)

- Output: Returns a list of tickets with essential fields including id, subject, status, priority, description, timestamps, and assignee information, along with pagination metadata

- Examples:
  - Get all tickets: `get_tickets(page=1, per_page=25)`
  - Get tickets for an organization: `get_tickets(organization_id=123)`
  - Get tickets requested by a user: `get_tickets(user_id=456, ticket_type="requested")`
  - Get recent tickets: `get_tickets(recent=true)`

### get_ticket

Retrieve a Zendesk ticket by its ID

- Input:
  - `ticket_id` (integer): The ID of the ticket to retrieve

### get_ticket_comments

Retrieve all comments for a Zendesk ticket by its ID

- Input:
  - `ticket_id` (integer): The ID of the ticket to get comments for

### create_ticket_comment

Create a new comment on an existing Zendesk ticket

- Input:
  - `ticket_id` (integer): The ID of the ticket to comment on
  - `comment` (string): The comment text/content to add
  - `public` (boolean, optional): Whether the comment should be public (defaults to true)

### create_ticket

Create a new Zendesk ticket

- Input:
  - `subject` (string): Ticket subject
  - `description` (string): Ticket description
  - `requester_id` (integer, optional)
  - `assignee_id` (integer, optional)
  - `priority` (string, optional): one of `low`, `normal`, `high`, `urgent`
  - `type` (string, optional): one of `problem`, `incident`, `question`, `task`
  - `tags` (array[string], optional)
  - `custom_fields` (array[object], optional)

### update_ticket

Update fields on an existing Zendesk ticket (e.g., status, priority, assignee)

- Input:
  - `ticket_id` (integer): The ID of the ticket to update
  - `subject` (string, optional)
  - `status` (string, optional): one of `new`, `open`, `pending`, `on-hold`, `solved`, `closed`
  - `priority` (string, optional): one of `low`, `normal`, `high`, `urgent`
  - `type` (string, optional)
  - `assignee_id` (integer, optional)
  - `requester_id` (integer, optional)
  - `tags` (array[string], optional)
  - `custom_fields` (array[object], optional)
  - `due_at` (string, optional): ISO8601 datetime

### list_users

List users with pagination support. Supports filtering by group or organization.

- Input:
  - `page` (integer, optional): Page number (defaults to 1)
  - `per_page` (integer, optional): Number of users per page, max 100 (defaults to 25)
  - `sort_by` (string, optional): Field to sort by - name, created_at, or updated_at (defaults to name)
  - `sort_order` (string, optional): Sort order - asc or desc (defaults to asc)
  - `group_id` (integer, optional): Filter users by group ID
  - `organization_id` (integer, optional): Filter users by organization ID

- Output: Returns a list of users with essential fields including id, name, email, role, active status, timestamps, and organization information, along with pagination metadata

- Examples:
  - Get all users: `list_users(page=1, per_page=25)`
  - Get users in a group: `list_users(group_id=123)`
  - Get users in an organization: `list_users(organization_id=456)`

### search_users

Search for users by query or external ID.

- Input:
  - `query` (string, optional): Search query using Zendesk search syntax (e.g., "name:John email:john@example.com"). Either `query` or `external_id` must be provided.
  - `external_id` (string, optional): External ID of the user to search for. Either `query` or `external_id` must be provided.
  - `page` (integer, optional): Page number (defaults to 1)
  - `per_page` (integer, optional): Number of users per page, max 100 (defaults to 25)

- Output: Returns a list of matching users with essential fields including id, name, email, role, active status, timestamps, organization information, and external_id, along with pagination metadata

- Examples:
  - Search by query: `search_users(query="name:John")`
  - Search by external ID: `search_users(external_id="ext_123")`

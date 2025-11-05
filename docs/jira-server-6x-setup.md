# Legacy Jira Server 6.x Setup

This guide explains how to configure `mcp-atlassian` to work with on-prem Jira Server v6.3.15 instances.

## Overview

Jira Server 6.3.15 uses REST API v2 and has different field formats compared to Cloud:
- **User identification**: Uses `name` and `key` instead of `accountId`
- **Authentication**: Basic Auth (username/password) or cookie-based sessions
- **API version**: `/rest/api/2` endpoints only
- **Pagination**: `startAt` / `maxResults` (max 50 per page)

## Configuration

### Environment Variables

Set the following environment variables for Server 6.x mode:

```bash
# Required: Set mode to server_6x
JIRA_MODE=server_6x

# Required: Jira instance URL
JIRA_URL=https://jira-server.example.com

# Required: Username
JIRA_USERNAME=admin

# Required: Password (for Basic Auth or cookie session)
JIRA_PASSWORD=your-password

# Optional: Authentication method (default: basic)
# Options: 'basic' or 'cookie'
JIRA_AUTH=basic

# Optional: SSL/TLS Configuration
# Path to CA bundle file for self-signed certificates
JIRA_CA_FILE=/path/to/ca-bundle.crt

# Optional: Disable SSL verification (NOT RECOMMENDED)
# Only use in testing environments
JIRA_TLS_INSECURE=false  # Default: false (secure)

# Optional: Project filter
JIRA_PROJECTS_FILTER=PROJ,DEV
```

### Authentication Methods

#### Basic Auth (Default)

```bash
JIRA_MODE=server_6x
JIRA_URL=https://jira-server.example.com
JIRA_USERNAME=admin
JIRA_PASSWORD=your-password
JIRA_AUTH=basic
```

#### Cookie-Based Session

```bash
JIRA_MODE=server_6x
JIRA_URL=https://jira-server.example.com
JIRA_USERNAME=admin
JIRA_PASSWORD=your-password
JIRA_AUTH=cookie
```

Cookie-based authentication:
- POSTs to `/rest/auth/1/session` to obtain JSESSIONID
- Automatically refreshes on 401 errors (max 1 retry)
- Logs out on shutdown (DELETE `/rest/auth/1/session`)

### SSL/TLS Configuration

For self-signed certificates, you have two options:

#### Option 1: Use CA Bundle File (Recommended)

```bash
JIRA_CA_FILE=/path/to/ca-bundle.crt
```

#### Option 2: Disable Verification (NOT RECOMMENDED)

```bash
JIRA_TLS_INSECURE=true
```

**Warning**: Disabling SSL verification is insecure and should only be used in testing environments.

## Example `.env` File

See `.env.server6x.example` for a complete example configuration file.

## Known Limitations

1. **No Personal Access Tokens (PAT)**: Server 6.3.15 does not support PAT tokens
2. **No OAuth**: OAuth 2.0 is not available for Server 6.x
3. **Limited Fields**: Some Cloud-only fields (e.g., `renderedFields`) are not available
4. **Pagination**: Maximum 50 results per page (enforced automatically)
5. **User Fields**: Uses `name` instead of `accountId` (automatically mapped)
6. **Email Address**: May be missing in some responses (handled gracefully)

## Feature Support

All core MCP capabilities are supported:

- ✅ Search issues by JQL with pagination
- ✅ Read issue details (all mapped fields)
- ✅ Create issues (minimal and with additional fields)
- ✅ Update issues (fields, assignee, reporter, etc.)
- ✅ Add comments
- ✅ List and perform transitions
- ✅ Get user profiles
- ✅ Get projects, boards, sprints

## Troubleshooting

### Authentication Fails

1. Verify `JIRA_USERNAME` and `JIRA_PASSWORD` are correct
2. Check if the user has API access permissions
3. For cookie auth, ensure `/rest/auth/1/session` endpoint is accessible
4. Check network connectivity and firewall rules

### SSL Certificate Errors

1. Use `JIRA_CA_FILE` to provide your CA bundle
2. Verify the certificate is valid and not expired
3. Only use `JIRA_TLS_INSECURE=true` in testing environments

### Field Mapping Issues

The mapper automatically converts:
- `accountId` → `name` (for requests)
- `name` → `accountId` (for responses, to maintain compatibility)

If you encounter issues, check the logs for mapping warnings.

### API Version Errors

Server 6.x mode automatically forces `/rest/api/2` endpoints. If you see v3 endpoint errors, verify `JIRA_MODE=server_6x` is set correctly.

## Testing

See the manual integration test checklist in the plan document for curl commands to verify your setup.

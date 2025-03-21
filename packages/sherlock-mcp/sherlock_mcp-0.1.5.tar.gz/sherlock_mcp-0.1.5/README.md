# Sherlock Domains MCP

An MCP server for buying and managing domains directly through AI assistants like Claude or Cursor.

## What is Sherlock Domains?

Sherlock Domains provides a simple way to search, buy, and manage domain names directly through AI assistants. No need for complex web interfaces or technical expertise - just chat with your AI and get your domain up and running.

## Prerequisites

- MCP Client like [Cursor](https://cursor.sh/) or [Claude Desktop](https://claude.ai/download)
- [UV](https://docs.astral.sh/uv/getting-started/installation/) installed
- A payment method through any L402-compatible client like [Fewsats](https://fewsats.com)

## Setting Up the MCP Server

### For Cursor

1. Open Cursor and go to Settings
2. Navigate to MCP Server Configuration
3. Add the following configuration:

```json
{
  "mcpServers": {
    "Sherlock Domains": {
      "command": "uvx",
      "args": [
        "sherlock-mcp"
      ]
    },
    "Fewsats": {
      "command": "env",
      "args": [
        "FEWSATS_API_KEY=YOUR_FEWSATS_API_KEY",
        "uvx",
        "fewsats-mcp"
      ]
    }
  }
}
```

Make sure to replace `YOUR_FEWSATS_API_KEY` with your actual API key from [Fewsats](https://app.fewsats.com/api-keys).

### For Claude Desktop

1. Find the configuration file:
   - On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the following configuration:

```json
"mcpServers": {
  "Sherlock Domains": {
    "command": "uvx",
    "args": [
      "sherlock-mcp"
    ]
  },
  "Fewsats": {
    "command": "env",
    "args": [
      "FEWSATS_API_KEY=YOUR_FEWSATS_API_KEY",
      "uvx",
      "fewsats-mcp"
    ]
  }
}
```

## Using Sherlock Domains with Your AI

Once configured, you can have natural conversations with your AI to manage domains:

### Searching for Domains

Simply ask your AI to search for available domains:

```
I want to buy a domain for my new podcast about AI. The podcast is called "AI Adventures". Can you find names that might be available?
```

### Buying a Domain

When you find a domain you like, just ask to buy it:

```
I want to buy ai-adventures.com
```

The AI will guide you through:
1. Setting up contact information (required by ICANN)
2. Reviewing pricing options
3. Processing payment via your L402-compatible client (like Fewsats)

### Managing DNS Records

After purchasing, you can easily manage your domain:

```
Please set up my domain ai-adventures.com to point to my GitHub Pages site
```

The AI will help configure the appropriate DNS records.

### Linking Your Account (Optional)

To manage your domains through the [Sherlock Domains](https://sherlockdomains.com) web interface:

```
I want to link my email address your@email.com to my Sherlock account
```

## Common DNS Configurations

Here are some example prompts for common DNS setups:

### GitHub Pages

```
Please configure my domain example.com for GitHub Pages with these IP addresses:
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153

And add a CNAME record for www pointing to my-username.github.io
```

### Vercel or Netlify

```
Please configure my domain for Vercel by adding a CNAME record for @ and www pointing to cname.vercel-dns.com
```

## Troubleshooting

- **DNS propagation delays:** DNS changes can take up to 24 hours to propagate globally
- **Payment issues:** Ensure your L402-compatible client (like Fewsats) has sufficient funds
- **MCP connection issues:** Verify your configuration and restart your AI application

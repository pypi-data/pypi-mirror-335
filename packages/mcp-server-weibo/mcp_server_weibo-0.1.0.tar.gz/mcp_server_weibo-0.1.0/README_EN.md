# Weibo MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server for fetching Weibo user information, posts, and search functionality. This server helps retrieve detailed user information, posts, and perform user searches on Weibo.

<a href="https://glama.ai/mcp/servers/weibo">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/weibo/badge" alt="Weibo MCP Server" />
</a>

## Installation

From source code:

```json
{
    "mcpServers": {
        "weibo": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/qinyuanpei/mcp-server-weibo.git",
                "mcp-server-weibo"
            ]
        }
    }
}
```

From package manager:

```json
{
    "mcpServers": {
        "weibo": {
            "command": "uvx",
            "args": ["mcp-server-weibo"],
        }
    }
}
```

## Components

### Tools

- `search_weibo_users`: Used to search for Weibo users
    - **Input:** `keyword`: Search keyword
    - **Output:** `WeiboUsers`: A list of Pydantic models containing basic user information

- `extract_weibo_profile`: Get detailed user information
    - **Input:** `user_id`: User ID
    - **Output:** `WeiboProfile`: A Pydantic model containing detailed user information

- `extract_weibo_feeds`: Get user posts
    - **Input:** `user_id`: User ID, `limit`: Number of posts to retrieve
    - **Output:** `WeiboFeeds`: A list of Pydantic models containing user post information

### Resources   

_No custom resources included_

### Prompts

_No custom prompts included_

## Requirements

- Python >= 3.8
- httpx >= 0.24.0
- pydantic >= 2.0.0
- fastmcp >= 0.1.0

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with Weibo and is intended for learning and research purposes only. 
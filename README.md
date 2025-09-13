[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/misiektoja-kill-process-mcp-badge.png)](https://mseep.ai/app/misiektoja-kill-process-mcp)

# kill-process-mcp 🔫

Cross-platform **MCP** (Model Context Protocol) server exposing tools to **list and kill OS processes** via natural language queries.

Perfect for shy ninjas who just want rogue processes gone!

> **"Find and nuke the damn CPU glutton choking my system!"**

<a href="https://glama.ai/mcp/servers/@misiektoja/kill-process-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@misiektoja/kill-process-mcp/badge" alt="kill-process-mcp MCP server" />
</a>

<a id="demo"></a>
## Demo

![kill-process-mcp-demo](https://raw.githubusercontent.com/misiektoja/kill-process-mcp/refs/heads/main/assets/kill-process-mcp-demo.gif)

<a id="tools"></a>
## Tools

The following tools are exposed to MCP clients:

- `process_list`: Lists running processes sorted by CPU or memory with optional name, user, status, CPU/memory thresholds, system-process filtering, sort order and limit
- `process_kill`: Terminates the selected process (with extreme prejudice!)

<a id="requirements"></a>
## Requirements

* MCP-compatible LLM client (like [Claude Desktop](https://claude.ai/download))
* OS: macOS/Windows/Linux
* Python 3.13 or higher
* [uv](https://github.com/astral-sh/uv)
* Libraries: `mcp` `psutil`

<a id="installation"></a>
## Installation

<a id="1-clone-the-repo-and-install"></a>
### 1. Clone the repo and install

```sh
git clone https://github.com/misiektoja/kill-process-mcp.git
cd kill-process-mcp
```

Install `uv` if missing:

```sh
pip install uv

# or on macOS: 
brew install uv
```

Install dependencies:

```sh
uv sync
```

<a id="2-configure-mcp-client"></a>
### 2. Configure MCP Client

Register the `kill-process-mcp` as an MCP server in your client.

For example, in Claude Desktop add the following to `claude_desktop_config.json` file:


  ```json
{
    "mcpServers":
    {
        "kill-process-mcp":
        {
            "command": "uv",
            "args":
            [
                "run",
                "--directory",
                "/path/to/kill-process-mcp",
                "kill_process_mcp.py"
            ],
            "type": "stdio"
        }
    }
}
  ```

Default `claude_desktop_config.json` location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Replace `/path/to/kill-process-mcp` with the actual path of your project folder (remember to escape backslash characters if you're on Windows, e.g.: `C:\\path\\to\\kill-process-mcp`)

Restart your LLM client and it should be able to talk to the `kill-process-mcp` server.

In `Claude Desktop` you can check if the server is installed by going to **Profile → Settings → Integrations**.

<a id="example-hit-contracts"></a>
## Example Hit Contracts

Here are some example prompts you can use with your MCP-compatible AI assistant when interacting with this MCP server:

- Kill the damn process slowing down my system!
- Check my top 5 CPU parasites and flag any that look like malware
- List the 3 greediest processes by RAM usage
- Exterminate every process with Spotify in its name
- List Alice's Python processes, max 10 entries
- Which processes are over 2% CPU and 100 MB RAM
- **anything else your imagination brings ...**

<a id="disclaimer"></a>
## Disclaimer

This MCP server is armed and dangerous. If you snipe the wrong process, that's on you. 

Proceed with caution.

<a id="change-log"></a>
## Change Log

See [RELEASE_NOTES.md](https://github.com/misiektoja/kill-process-mcp/blob/main/RELEASE_NOTES.md) for details.

<a id="license"></a>
## License

Licensed under GPLv3. See [LICENSE](https://github.com/misiektoja/kill-process-mcp/blob/main/LICENSE).
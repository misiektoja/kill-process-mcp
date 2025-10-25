# kill-process-mcp release notes

This is a high-level summary of the most important changes.

# Changes in 1.1 (25 Oct 2025)

**Features and Improvements**:

- **NEW:** `kill-process-mcp` can now be installed and launched directly using `uvx`, no manual setup required
- **IMPROVE:** Enhanced process_list parameter validation and error handling, allowing stringified numeric args for better MCP client compatibility (fixes [#6](https://github.com/misiektoja/kill-process-mcp/issues/6))

**Bug fixes**:

- **BUGFIX:** Removed deprecated tool_homepage argument from FastMCP initialization (fixes [#4](https://github.com/misiektoja/kill-process-mcp/issues/4), thanks [@magicman-dot](https://github.com/magicman-dot))
- **BUGFIX:** Fixed occasional crashes on macOS by using correct rusage struct version and safer sleep timing

# Changes in 1.0 (01 Jul 2025)

**Features and Improvements**:

- **NEW:** Introduced MCP `process_list` tool to list running processes with optional filtering, sorting and limit
- **NEW:** Introduced MCP `process_kill` tool to kill the selected process
- **NEW:** Implemented macOS-only helper for Activity Monitor-style physical memory reporting with fallback to RSS and USS memory metrics on Windows and Linux
- **IMPROVE:** Excluded processes owned by system users by default

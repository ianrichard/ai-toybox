# AI Toybox

AI Toybox is an experimental playground for generative AI, focused on rapid prototyping and testing of Model Context Protocol (MCP) tools and agent workflows.

## What is this?

- **Chat app with tool use:** Try out LLMs and MCP tools in a unified chat interface.
- **MCP server template:** Quickly build and test your own MCP tools, decoupled from the main app.
- **Plug-and-play environment:** No need to fuss with complex configuration—just add your tool, wire it up, and experiment.

## Why?

This project is meant as a low-friction sandbox for anyone interested in building, sharing, or exploring custom MCP tools and agent behaviors. It's not intended for production or long-term maintenance—just a space to play, learn, and collaborate.

> **Note:** Putting MCP servers directly inside the main app can quickly lead to headaches—managing ports, Docker containers, dependencies, and environments gets messy fast. In real-world projects, you'll almost always want your MCP tool as a separate module anyway. This repo gives you that separation from the start, so you can focus on building and testing tools without fighting configuration issues.

## Structure

- `app/` – The main chat app and agent API (see `app/README.md` for details)
- `mcp-server-template/` – Example MCP server and tools (see `mcp-server-template/README.md`)

## Getting Started

See the `README.md` files in each subdirectory for setup and usage instructions.

---

Open to contributions, ideas, and experiments!
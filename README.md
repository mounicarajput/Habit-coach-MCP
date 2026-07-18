# AI Habit Coach: MCP Server (Free & Open-Source)

A personal AI habit coach that runs on your own laptop, using a free open-source
model (Qwen3 via Ollama) instead of a paid API.

Tell it "I meditated today" in plain English — it logs it, tracks your streak,
and can give you an honest weekly recap. No subscription. Nothing leaves your machine.

📖 **Full step-by-step guide:** [How to Build Your First MCP Server](https://monikarajput.substack.com/p/how-to-build-your-first-mcp-server)

## What it does

- **`log_habit`** — record that you did a habit today
- **`get_streak`** — current streak + best streak for a habit
- **`list_habits`** — everything you're tracking, at a glance
- **`habits://all`** — resource exposing your full habit history
- **`weekly_habit_recap`** — a saved prompt for an honest weekly check-in

## Quick start

```bash
# 1. Install Ollama and start it
brew install ollama
ollama serve

# 2. Pull a model (use 4b if you have 8GB RAM, 8b if you have 16GB+)
ollama pull qwen3:4b

# 3. Set up the project
python3 -m venv venv
source venv/bin/activate
pip install mcp ollama

# 4. (Optional) test the server on its own
npx @modelcontextprotocol/inspector python3 server.py

# 5. Run it
python3 client.py
```

Try:
```
> I meditated for 10 minutes today
> what's my meditation streak?
> how am I doing overall?
```

## Files

- `server.py` — the MCP server: tools, a resource, and a prompt
- `client.py` — connects the server to a local Ollama model
- `workspace/` — created automatically; your habit log lives here

## Why open-source instead of a paid model

Any MCP server works with any MCP-compatible model — Claude, an open-source
model, whatever ships next. This project uses Ollama + Qwen3 so the whole
thing runs for $0, entirely on your own machine.

Read the full breakdown, line by line, in the [Substack article](https://monikarajput.substack.com/p/how-to-build-your-first-mcp-server).

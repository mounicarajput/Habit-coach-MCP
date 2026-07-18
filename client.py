import asyncio
import json

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "qwen3:4b"
SERVER_COMMAND = "python3"
SERVER_ARGS = ["server.py"]

SYSTEM_PROMPT = (
    "You are an encouraging, practical habit coach. You have tools to log "
    "habits, check streaks, and list everything being tracked. Use the "
    "tools whenever the user mentions doing (or skipping) a habit, or asks "
    "about their progress. Never claim to have logged or calculated "
    "something unless you actually called the tool."
)

def mcp_tools_to_ollama_format(mcp_tools) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema,
            },
        }
        for t in mcp_tools
    ]

async def run_agent_loop(session: ClientSession, ollama_tools: list[dict], user_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for _ in range(6):
        response = ollama.chat(model=MODEL, messages=messages, tools=ollama_tools)
        msg = response["message"]
        messages.append(msg)

        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            return msg.get("content", "")

        for call in tool_calls:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)

            print(f"  [tool call] {name}({args})")
            result = await session.call_tool(name, args)
            result_text = "\n".join(b.text for b in result.content if hasattr(b, "text"))
            messages.append({"role": "tool", "content": result_text, "name": name})

    return "Stopped after too many tool calls — the model may be stuck in a loop."

async def main():
    params = StdioServerParameters(command=SERVER_COMMAND, args=SERVER_ARGS)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_response = await session.list_tools()
            ollama_tools = mcp_tools_to_ollama_format(tools_response.tools)
            print(f"Connected. Tools available: {[t['function']['name'] for t in ollama_tools]}\n")

            print("Try: 'I meditated for 10 minutes today' or 'what's my gym streak?'")
            print("Type 'quit' to exit.\n")
            while True:
                user_message = input("> ").strip()
                if user_message.lower() in ("quit", "exit"):
                    break
                if not user_message:
                    continue
                answer = await run_agent_loop(session, ollama_tools, user_message)
                print(f"\n{answer}\n")


if __name__ == "__main__":
    asyncio.run(main())


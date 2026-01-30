import asyncio
from typing import Optional, Dict, Any, List
from contextlib import AsyncExitStack
import sys
import os
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("-" * 30)
if os.getenv("GROQ_API_KEY"):
    print(f"DEBUG: API Key loaded successfully (starts with: {os.getenv('GROQ_API_KEY')[:10]}...)")
else:
    print("DEBUG: ERROR - GROQ_API_KEY environment variable is NOT set after load_dotenv().")
    sys.exit(1)
print("-" * 30)


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.chat_history: List[Dict[str, Any]] = []
        self.target_tool_name = "get_latest_rates"
        self.tool_specific_log = []

        try:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        except Exception as e:
            print(f"ERROR initializing Groq Client: {e}")
            sys.exit(1)

    async def connect_to_server(self, server_script_path: str):

        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        resources_response = await self.session.list_resources()
        self.available_resources = resources_response.resources

        from mcp.types import Resource

        tool_log_resource = Resource(
            name=f"Log: {self.target_tool_name}",
            uri=f"internal://logs/{self.target_tool_name}",
            mimeType="application/json",
            description=f"Exclusive history for {self.target_tool_name} usage."
        )
        self.available_resources.append(tool_log_resource)

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

        prompts_response = await self.session.list_prompts()
        self.available_prompts = prompts_response.prompts
        print("Available Prompts:", [prompt.name for prompt in self.available_prompts])

    async def process_query(self, query: str) -> str:
        self.chat_history.append(
            {"role": "user", "content": query}
        )

        response = await self.session.list_tools()

        tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in response.tools
        ]

        final_text = []

        while True:
            try:
                api_response = self.client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=self.chat_history,
                    tools=tools_schema if tools_schema else None,
                    tool_choice="auto" if tools_schema else "none"
                )
            except Exception as e:
                return f"API Call failed: {e}"

            response_message = api_response.choices[0].message
            
            message_dict = {
                "role": response_message.role,
                "content": response_message.content
            }
            if response_message.tool_calls:
                message_dict["tool_calls"] = response_message.tool_calls
            
            self.chat_history.append(message_dict)

            if response_message.content:
                final_text.append(response_message.content)

            tool_calls = response_message.tool_calls

            if not tool_calls:
                break

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    content = result.content[0].text if result.content else ""

                    if tool_name == self.target_tool_name:
                        entry = {
                            "timestamp": datetime.now().isoformat(),
                            "arguments": tool_args,
                            "result": content
                        }
                        self.tool_specific_log.append(entry)
                        print(f"   [Log] Saved entry to {tool_name} history.")

                except Exception as e:
                    content = f"Error executing tool: {e}"

                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                self.chat_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(content)
                })

        return "\n".join(final_text)

    async def use_prompt(self, prompt_name: str, arguments: Optional[Dict[str, Any]] = None):
        try:
            if arguments:
                for key, value in arguments.items():
                    if isinstance(value, list):
                        arguments[key] = ",".join(map(str, value))
                    else:
                        arguments[key] = str(value)

            result = await self.session.get_prompt(prompt_name, arguments)

            if not result.messages:
                return

            prompt_text = "\n".join([m.content.text for m in result.messages if hasattr(m.content, 'text')])
            print(f"\n--- Executing Prompt: {prompt_name} ---\n{prompt_text}")

            response = await self.process_query(prompt_text)
            print("\nResponse:\n" + response)

        except Exception as e:
            print(f"Error fetching prompt '{prompt_name}': {e}")

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries\n"
              "'/prompts' to show available prompts\n"
              "'/clear' to clear chat history\n"
              "'/read' to read tool history\n"
              "'/use' to create a prompt using a template\n"
              "'/exit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == '/exit':
                    break

                if query.lower() == '/prompts':
                    if hasattr(self, 'available_prompts') and self.available_prompts:
                        print("\nAvailable Prompts")
                        for p in self.available_prompts:
                            print(f"* {p.name}: {p.description}")
                    else:
                        print("No prompts available.")
                    continue

                if query.lower() == '/clear':
                    self.chat_history = []
                    print("Memory cleared.")
                    continue

                if query.lower().startswith('/read'):
                    target_uri = f"internal://logs/{self.target_tool_name}"
                    
                    parts = query.split(' ', 1)
                    
                    if len(parts) == 1:
                        uri_to_read = target_uri
                    else:
                        uri_to_read = parts[1].strip()

                    if uri_to_read == target_uri:
                        print(f"\nHistory for '{self.target_tool_name}'")
                        if self.tool_specific_log:
                            print(json.dumps(self.tool_specific_log, indent=2, default=str))
                        else:
                            print("(Log is empty)")
                    else:
                        print(f"Unknown resource URI: {uri_to_read}")
                        print(f"Available default: {target_uri}")
                    continue

                if query.lower().startswith('/use'):
                    parts = query.split(' ', 2)
                    if len(parts) < 2:
                        print("Usage: /use <prompt_name> [json_arguments]")
                        continue

                    p_name = parts[1]
                    p_args = None

                    if len(parts) > 2:
                        try:
                            p_args = json.loads(parts[2])
                        except json.JSONDecodeError:
                            print("Error: Arguments must be valid JSON.")
                            continue

                    await self.use_prompt(p_name, p_args)
                    continue

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())

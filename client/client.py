import asyncio
from typing import Optional, Dict, Any, List
from contextlib import AsyncExitStack
import sys
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

print("-" * 30)
if os.getenv("GEMINI_API_KEY"):
    print(f"DEBUG: API Key loaded successfully (starts with: {os.getenv('GEMINI_API_KEY')[:12]}...)")
else:
    print("DEBUG: ERROR - GEMINI_API_KEY environment variable is NOT set after load_dotenv().")
    sys.exit(1)
print("-" * 30)


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        try:
            self.client = genai.Client()
        except Exception as e:
            print(f"ERROR initializing Gemini Client: {e}")
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

        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:

        messages: List[types.Content] = [
            types.Content(role="user", parts=[types.Part.from_text(text=query)])
        ]

        response = await self.session.list_tools()

        function_declarations: List[types.FunctionDeclaration] = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=tool.inputSchema
            ) for tool in response.tools
        ]

        config = types.GenerateContentConfig(
            tools=[{"function_declarations": function_declarations}]
        )

        final_text = []

        while True:
            response: types.GenerateContentResponse = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=config,
            )

            if not response.candidates:
                if response.prompt_feedback.block_reason:
                    return f"ERROR: Prompt blocked due to {response.prompt_feedback.block_reason.name}"
                return "ERROR: No response candidates received."

            if response.text:
                final_text.append(response.text)

            function_calls = response.function_calls

            if not function_calls:
                break

            tool_results = []

            messages.append(response.candidates[0].content)

            for call in function_calls:
                tool_name = call.name
                tool_args = dict(call.args)

                result = await self.session.call_tool(tool_name, tool_args)

                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                tool_results.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"content": result.content}
                    )
                )

            messages.append(types.Content(role="tool", parts=tool_results))

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

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
## Running

```powershell
uv init .
uv venv
.venv\Scripts\activate
uv add mcp mcp[cli] python-dotenv httpx google-genai
del main.py
uv run .\client\client.py .\server\server.py
```

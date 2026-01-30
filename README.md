## Running

```powershell
uv init .
uv venv
.venv\Scripts\activate
uv add "mcp[cli]" python-dotenv httpx groq
del main.py
uv run .\client\client.py .\server\server.py
```

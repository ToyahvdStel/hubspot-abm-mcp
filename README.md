# hubspot-abm-mcp

A read-only MCP server that lets Claude query HubSpot CRM data. Built as a hands-on project for AI-driven GTM and RevOps workflows.

It exposes one tool, `get_companies`, which returns companies from HubSpot with these fields: `name`, `domain`, `industry`, `numberofemployees`, `country`. It can only read data; it never changes anything in HubSpot.

Results are fetched page by page (100 companies per request), so accounts with more than 100 companies are fully supported. The optional `limit` argument sets the maximum number of companies to return in total (default 1000, maximum 10,000).

## Setup (Windows, PowerShell)

1. **Create a HubSpot Private App token**
   HubSpot → Settings → Integrations → Private Apps → Create private app.
   Under *Scopes*, tick only `crm.objects.companies.read`. Create the app and copy the token.

2. **Install the dependencies** (from this folder)
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Add your token**
   ```powershell
   Copy-Item .env.example .env
   ```
   Open `.env` and replace the placeholder with your token:
   ```
   HUBSPOT_TOKEN=your-token-here
   ```
   `.env` is listed in `.gitignore`, so it is never committed.

4. **Register the server in Claude Code**
   ```powershell
   claude mcp add hubspot-abm -- "$PWD\.venv\Scripts\python.exe" "$PWD\server.py"
   ```
   Check it with `claude mcp list`.

## Try it

Start Claude Code and ask:

> Which companies are in my HubSpot account?

## Files

| File | Purpose |
|---|---|
| `server.py` | The MCP server and the `get_companies` tool |
| `requirements.txt` | Python packages (`mcp` is pinned below v2, which renamed `FastMCP`) |
| `.env.example` | Template for your local `.env` |

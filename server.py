"""A minimal, read-only MCP server that exposes HubSpot companies to Claude."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load HUBSPOT_TOKEN from the .env file next to this script, regardless of
# which folder Claude Code starts the server from.
load_dotenv(Path(__file__).parent / ".env")

HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects/companies"
PROPERTIES = ["name", "domain", "industry", "numberofemployees", "country"]
PAGE_SIZE = 100  # HubSpot allows at most 100 records per request
MAX_LIMIT = 10_000  # safety cap so one question can't pull the whole CRM


mcp = FastMCP("hubspot-abm")


@mcp.tool()
def get_companies(limit: int = 1000) -> list[dict]:
    """Return companies from the HubSpot CRM (read-only).

    Each company has: id, name, domain, industry, numberofemployees, country.
    Results are fetched page by page, so accounts with more than 100
    companies are fully supported. `limit` is the maximum number of
    companies to return in total (1-10000, default 1000).
    """
    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        raise RuntimeError(
            "HUBSPOT_TOKEN is not set. Add it to the .env file in the project folder."
        )

    limit = max(1, min(limit, MAX_LIMIT))
    companies: list[dict] = []
    after = None  # HubSpot's bookmark for "the next page"

    with httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=30) as client:
        while len(companies) < limit:
            params = {
                "limit": min(PAGE_SIZE, limit - len(companies)),
                "properties": ",".join(PROPERTIES),
            }
            if after:
                params["after"] = after

            response = client.get(HUBSPOT_URL, params=params)
            if response.status_code == 401:
                raise RuntimeError("HubSpot rejected the token (401). Check HUBSPOT_TOKEN.")
            if response.status_code == 403:
                raise RuntimeError(
                    "HubSpot token lacks permission (403). Enable the "
                    "crm.objects.companies.read scope on your private app."
                )
            response.raise_for_status()

            data = response.json()
            companies.extend(
                {"id": item["id"], **{p: item["properties"].get(p) for p in PROPERTIES}}
                for item in data.get("results", [])
            )

            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:  # no next page: we have everything
                break

    return companies


if __name__ == "__main__":
    mcp.run(transport="stdio")

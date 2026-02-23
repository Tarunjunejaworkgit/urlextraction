import os
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from mcp.server.fastmcp import FastMCP

# ----------------------------
# Configuration
# ----------------------------
DUCKDUCKGO_URL = "https://html.duckduckgo.com/html/"
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))
USER_AGENT = "Mozilla/5.0 (compatible; BusinessWebsiteFinder/1.0)"

# ----------------------------
# Create MCP instance
# ----------------------------
mcp = FastMCP("Business Website Finder")


# ----------------------------
# DuckDuckGo Search
# ----------------------------
async def search_duckduckgo(query: str, max_results: int = MAX_RESULTS) -> List[str]:
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(headers=headers, timeout=REQUEST_TIMEOUT) as client:
        resp = await client.post(DUCKDUCKGO_URL, data={"q": query})
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    results: List[str] = []
    for link in soup.select("a.result__a"):
        href = link.get("href")
        if href and href.startswith("http"):
            results.append(href)
            if len(results) >= max_results:
                break

    return results


# ----------------------------
# MCP TOOL
# ----------------------------
@mcp.tool()
async def find_company_website(company_name: str) -> dict:
    """
    MCP tool: Find website of a company
    """

    query = f"{company_name.strip()} official website"
    results = await search_duckduckgo(query)

    official_site: Optional[str] = results[0] if results else None

    return {
        "business_name": company_name,
        "official_website": official_site,
        "searched_results_count": len(results),
    }


# ----------------------------
# FastAPI wrapper (for testing + Azure)
# ----------------------------
app = FastAPI(
    title="Business Website Finder MCP Server",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"status": "running", "mcp_endpoint": "/mcp"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ⭐ MOUNT MCP SERVER (SSE transport)
app.mount("/mcp", mcp.sse_app)


# ----------------------------
# Optional REST endpoint (for testing)
# ----------------------------
@app.get("/find-website")
async def find_website(business_name: str = Query(...)):
    query = f"{business_name.strip()} official website"
    results = await search_duckduckgo(query)

    official_site: Optional[str] = results[0] if results else None

    return {
        "business_name": business_name,
        "official_website": official_site,
        "searched_results_count": len(results),
    }
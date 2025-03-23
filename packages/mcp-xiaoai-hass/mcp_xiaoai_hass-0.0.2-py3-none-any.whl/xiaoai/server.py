# server.py
import os
import requests

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("mcp-xiaoai-hass")

@mcp.tool(
    description="Smart Home Assistant / 小爱同学，您的智能家居助手",
)
def execute_text_directive(text: str) -> str:
    host = os.getenv("HASS_HOST")
    entity_id = os.getenv("HASS_XIAOAI_ENTITY_ID")
    token = os.getenv("HASS_TOKEN")

    url = f"https://{host}/api/services/xiaomi_miot/intelligent_speaker"
    payload = {
        "entity_id": entity_id,
        "execute": True,
        "silent": True,
        "text": text,
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return "OK"


def main():
    mcp.run()

# MCP XiaoAi HASS Server

Use Hass API to control XiaoAi

# Installation

Recommend use `uvx` to setup

## requirements
You need three components installed already:
home assistant / miot
and a xiaomi ai speaker

Use uvx to install this packages
> uvx mcp-xiaoai-hass


# Configuration & Usage
Use client like Cherry Studio


## Environment Variables
HASS_HOST -- home assistant host
HASS_XIAOAI_ENTITY_ID -- home assistant entity id
HASS_TOKEN -- home assistant token

eg:
HASS_HOST=hass.home.geminiwen.com
HASS_XIAOAI_ENTITY_ID=media_player.xiaomi_lx05_0ed6_play_control
HASS_TOKEN=home_assistant_token

"""
JUHE API Weather FastMCP Server
"""

from pydantic import Field
import mcp.types as types
from mcp.server.fastmcp import FastMCP
import httpx
import os

# Create server
mcp = FastMCP("jweather-mcp-server", title="JUHE API Weather MCP Server", description="Weather API from JUHE")

JUHE_WEATHER_API_BASE = "http://apis.juhe.cn/simpleWeather/"
JUHE_WEATHER_API_KEY = os.environ.get("JUHE_WEATHER_API_KEY")

@mcp.tool(name="query_weather", description="根据城市、地区、区县名称查询当地实时天气预报情况")
async def query_weather(
    city: str = Field(description="查询的城市名称，如北京、上海、广州、深圳、泰顺等；城市或区县或地区名使用简写，严格按照规范填写，否则会导致查询失败")
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """根据城市、地区、区县名称查询当地实时天气预报情况"""
    url = f"{JUHE_WEATHER_API_BASE}/query"
    params = {
        "city": city,
        "key": JUHE_WEATHER_API_KEY
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        data = response.json()
        if data["error_code"] == 0:
            result = data["result"]
            return [
                types.TextContent(
                    type="text",
                    text=f"{result}"
                )
            ]
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: {data['reason']}"
                )
            ]


async def main():
    # mcp.run(transport="stdio")
    await mcp.run_stdio_async()
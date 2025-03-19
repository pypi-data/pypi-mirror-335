"""
JUHE API Exchange Rates FastMCP Server
"""

from pydantic import Field
import mcp.types as types
from mcp.server.fastmcp import FastMCP
import httpx
import os

# Create server
mcp = FastMCP("jexchange-mcp-server", title="JUHE API Exchange Rates MCP Server", description="Exchange Rates API from JUHE")

JUHE_EXCHANGE_API_BASE = "http://op.juhe.cn/onebox/exchange/"
JUHE_EXCHANGE_API_KEY = os.environ.get("JUHE_EXCHANGE_API_KEY")

@mcp.tool(name="query_exchange_rates", description="根据货币的三位字母代码查询两者之间的兑换汇率")
async def query_exchange_rates(
    from_code: str = Field(description="您希望转换的货币的三位字母货币代码。如：CNY"),
    to_code : str = Field(description="您希望转换为目标货币的三位字母货币代码。如：USD")
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """根据城市、地区、区县名称查询当地实时天气预报情况"""
    url = f"{JUHE_EXCHANGE_API_BASE}/currency"
    params = {
        "version": "2",
        "from": from_code,
        "to": to_code,
        "key": JUHE_EXCHANGE_API_KEY
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
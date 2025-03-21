import base64
import logging
from mcp.server.fastmcp import FastMCP
from rapidocr import RapidOCR
from typing import List
from mcp.types import TextContent

logging.disable(logging.INFO)

mcp = FastMCP("RapidOCR MCP Server")
engine = RapidOCR()


@mcp.tool()
def ocr_by_content(base64_data: str) -> List[TextContent]:
    """使用base64编码的图片内容进行OCR识别。

    Args:
        base64_data: base64编码的图片内容字符串

    Returns:
        List[TextContent]: 识别出的文本内容列表
    """
    if not base64_data:
        return []
    
    img = base64.b64decode(base64_data)
    result = engine(img)
    if result:
        return list(map(lambda x: TextContent(type="text", text=x), result.txts))
    return []


@mcp.tool()
def ocr_by_path(path: str) -> List[TextContent]:
    """使用图片文件路径进行OCR识别。

    Args:
        path: 图片文件的路径

    Returns:
        List[TextContent]: 识别出的文本内容列表
    """
    if not path:
        return []
    
    result = engine(path)
    if result:
        return list(map(lambda x: TextContent(type="text", text=x), result.txts))
    return []


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()

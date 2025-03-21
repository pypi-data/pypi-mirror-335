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
    """Perform OCR recognition on base64 encoded image content.

    Args:
        base64_data: Base64 encoded image content string

    Returns:
        List[TextContent]: List of recognized text content
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
    """Perform OCR recognition on an image file.

    Args:
        path: Path to the image file

    Returns:
        List[TextContent]: List of recognized text content
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

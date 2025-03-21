# RapidOCR MCP Server

A MCP server based on RapidOCR, providing an easy-to-use OCR interface.

## Usage

```bash
uvx run rapidocr-mcp
```

## Available Methods

* ocr_by_content
Perform OCR on an image content. Args: base64_data (str): The base64 encoded image content. Returns: List[TextContent]: A list of text content.

* ocr_by_path
Perform OCR on an image file. Args: path (str): The path to the image file. Returns: List[TextContent]: A list of text content.
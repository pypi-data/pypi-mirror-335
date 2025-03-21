from setuptools import setup, find_packages
from rapidocr_mcp import __version__

setup(
    name="rapidocr-mcp",
    version=__version__,
    keywords=["ocr", "rapidocr", "mcp"],
    description="RapidOCR MCP Server for OCR processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="z4none",
    author_email="z4none@gmail.com",
    url="https://github.com/z4none/rapidocr-mcp",
    packages=find_packages(),
    install_requires=[
        "mcp[cli] >= 1.4.1",
        "rapidocr >= 2.0.3",
        "requests >= 2.32.3",
    ],
    entry_points={
        "console_scripts": [
            "rapidocr-mcp = rapidocr_mcp.main:main",
        ],
    },
)

from mcp.types import Tool
from pydantic import BaseModel, Field


class PageFetchRequest(BaseModel):
    url: str = Field(..., description="URL to fetch")
    mode: str = Field(
        "basic", description="Fetching mode (basic, stealth, or max-stealth)"
    )
    format: str = Field("markdown", description="Output format (html or markdown)")
    max_length: int = Field(
        5000,
        description="Maximum number of characters to return.",
        gt=0,
        lt=1000000,
        title="Max Length",
    )
    start_index: int = Field(
        0,
        description="On return output starting at this character index, useful if a previous fetch was truncated and more content is required.",
        ge=0,
        title="Start Index",
    )


class PatternFetchRequest(BaseModel):
    url: str = Field(..., description="URL to fetch")
    mode: str = Field(
        "basic", description="Fetching mode (basic, stealth, or max-stealth)"
    )
    format: str = Field("markdown", description="Output format (html or markdown)")
    max_length: int = Field(
        5000,
        description="Maximum number of characters to return.",
        gt=0,
        lt=1000000,
        title="Max Length",
    )
    search_pattern: str = Field(
        ...,
        description="Regular expression pattern to search for in the content",
    )
    context_chars: int = Field(
        200,
        description="Number of characters to include before and after each match",
        ge=0,
    )


s_fetch_page_tool = Tool(
    name="s-fetch-page",
    description="Fetches a complete web page with pagination support. "
    "Retrieves content from websites with bot-detection avoidance. "
    "For best performance, start with 'basic' mode (fastest), then only escalate to "
    "'stealth' or 'max-stealth' modes if basic mode fails. "
    "Content is returned as 'METADATA: {json}\\n\\n[content]' where metadata includes "
    "length information and truncation status.",
    inputSchema=PageFetchRequest.model_json_schema(),
)

s_fetch_pattern_tool = Tool(
    name="s-fetch-pattern",
    description="Extracts content matching regex patterns from web pages. "
    "Retrieves specific content from websites with bot-detection avoidance. "
    "For best performance, start with 'basic' mode (fastest), then only escalate to "
    "'stealth' or 'max-stealth' modes if basic mode fails. "
    "Returns matched content as 'METADATA: {json}\\n\\n[content]' where metadata includes "
    "match statistics and truncation information. Each matched content chunk is "
    "delimited with '॥๛॥' and prefixed with '[Position: start-end]' indicating its byte position "
    "in the original document, allowing targeted follow-up requests with s-fetch-page using "
    "specific start_index values.",
    inputSchema=PatternFetchRequest.model_json_schema(),
)

from functools import reduce
from re import compile
from re import error as re_error
from typing import Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from scrapling_fetch_mcp._markdownify import _CustomMarkdownify
from scrapling_fetch_mcp._scrapling import browse_url
from scrapling_fetch_mcp.tools import PageFetchRequest, PatternFetchRequest


class UrlFetchResponse(BaseModel):
    content: str
    metadata: "UrlFetchResponse.Metadata" = Field(
        default_factory=lambda: UrlFetchResponse.Metadata(),
        description="Metadata about the content retrieval",
    )

    class Metadata(BaseModel):
        total_length: int
        retrieved_length: int
        is_truncated: bool
        percent_retrieved: float
        start_index: Optional[int] = None
        match_count: Optional[int] = None


def _html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for script in soup(["script", "style"]):
        script.extract()
    body_elm = soup.find("body")
    return _CustomMarkdownify().convert_soup(body_elm if body_elm else soup)


def _search_content(
    content: str, pattern: str, context_chars: int = 200
) -> tuple[str, int]:
    try:
        matches = list(compile(pattern).finditer(content))
        if not matches:
            return "", 0
        chunks = [
            (
                max(0, match.start() - context_chars),
                min(len(content), match.end() + context_chars),
            )
            for match in matches
        ]
        merged_chunks = reduce(
            lambda acc, chunk: (
                [*acc[:-1], (acc[-1][0], max(acc[-1][1], chunk[1]))]
                if acc and chunk[0] <= acc[-1][1]
                else [*acc, chunk]
            ),
            chunks,
            [],
        )
        result_sections = [
            f"॥๛॥\n[Position: {start}-{end}]\n{content[start:end]}" 
            for start, end in merged_chunks
        ]
        return "\n".join(result_sections), len(matches)
    except re_error as e:
        return f"ERROR: Invalid regex pattern: {str(e)}", 0


def _search_req(
    full_content: str, request: PatternFetchRequest
) -> tuple[str, UrlFetchResponse.Metadata]:
    original_length = len(full_content)
    matched_content, match_count = _search_content(
        full_content, request.search_pattern, request.context_chars
    )
    if not matched_content:
        return "", UrlFetchResponse.Metadata(
            total_length=original_length,
            retrieved_length=0,
            is_truncated=False,
            percent_retrieved=0,
            match_count=0,
        )
    truncated_content = matched_content[: request.max_length]
    is_truncated = len(matched_content) > request.max_length
    metadata = UrlFetchResponse.Metadata(
        total_length=original_length,
        retrieved_length=len(truncated_content),
        is_truncated=is_truncated,
        percent_retrieved=round((len(truncated_content) / original_length) * 100, 2)
        if original_length > 0
        else 100,
        match_count=match_count,
    )
    return truncated_content, metadata


def _regular_req(
    full_content: str, request: PageFetchRequest
) -> tuple[str, UrlFetchResponse.Metadata]:
    total_length = len(full_content)
    truncated_content = full_content[
        request.start_index : request.start_index + request.max_length
    ]
    is_truncated = total_length > (request.start_index + request.max_length)
    metadata = UrlFetchResponse.Metadata(
        total_length=total_length,
        retrieved_length=len(truncated_content),
        is_truncated=is_truncated,
        percent_retrieved=round((len(truncated_content) / total_length) * 100, 2)
        if total_length > 0
        else 100,
        start_index=request.start_index,
    )
    return truncated_content, metadata


def _extract_content(page, request) -> str:
    is_markdown = request.format == "markdown"
    return _html_to_markdown(page.html_content) if is_markdown else page.html_content


async def fetch_page(request: PageFetchRequest) -> UrlFetchResponse:
    page = await browse_url(request.url, request.mode)
    full_content = _extract_content(page, request)
    content, metadata = _regular_req(full_content, request)
    return UrlFetchResponse(content=content, metadata=metadata)


async def fetch_pattern(request: PatternFetchRequest) -> UrlFetchResponse:
    page = await browse_url(request.url, request.mode)
    full_content = _extract_content(page, request)
    content, metadata = _search_req(full_content, request)
    return UrlFetchResponse(content=content, metadata=metadata)

"""Parallel Search runtime adapter."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import os
from typing import Any
from parallel import Parallel

@dataclass
class SearchEvidence:
    title: str
    url: str
    excerpt: str = ""
    source: str = "parallel"

class ParallelSearchService:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("PARALLEL_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("PARALLEL_API_KEY is required for live Parallel Search.")
        self.client = Parallel(api_key=self.api_key)

    def search(self, objective: str, search_queries: list[str], *, max_results: int = 8) -> list[dict[str, Any]]:
        if not search_queries:
            raise ValueError("At least one search query is required.")
        response = self.client.search(objective=objective, search_queries=search_queries[:3], mode="basic")
        raw = getattr(response, "results", None)
        if raw is None and isinstance(response, dict):
            raw = response.get("results", [])
        normalized = []
        for item in (raw or [])[:max_results]:
            title = getattr(item, "title", None); url = getattr(item, "url", None); excerpt = getattr(item, "excerpt", None)
            if isinstance(item, dict):
                title = title or item.get("title"); url = url or item.get("url"); excerpt = excerpt or item.get("excerpt") or item.get("snippet")
            if url:
                normalized.append(asdict(SearchEvidence(title=title or url, url=url, excerpt=excerpt or "")))
        return normalized

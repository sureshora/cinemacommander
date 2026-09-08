from .parallel_search import ParallelSearchService

def parallel_web_search(objective: str, search_queries: list[str]) -> dict:
    service = ParallelSearchService()
    evidence = service.search(objective=objective, search_queries=search_queries, max_results=8)
    return {"provider": "Parallel Search API", "result_count": len(evidence), "evidence": evidence}

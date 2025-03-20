from concurrent.futures import ThreadPoolExecutor
from duckduckgo_search import DDGS


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def _handle_single_query(query, max_urls=10, unique=True, advanced=False):
    try:
        with DDGS() as ddgs:
            # Use backend="lite" as it's more reliable than the default API
            results = list(ddgs.text(
                query,
                max_results=max_urls,
                backend="lite"
            ))

        processed_results = []
        seen_urls = set()

        for result in results:
            url = result['href']

            # Skip if URL already seen and unique is True
            if unique and url in seen_urls:
                continue

            # Only include URLs starting with http
            if not url.startswith('http'):
                continue

            seen_urls.add(url)

            if advanced:
                processed_results.append(
                    SearchResult(
                        url=url,
                        title=result['title'],
                        description=result['body']
                    )
                )
            else:
                processed_results.append(url)

            if len(processed_results) >= max_urls:
                break

        return processed_results
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []


def duckduckgo(query: str | list, max_urls=10, unique=True, advanced=False) -> list[str] | list[SearchResult]:
    """
    Search DuckDuckGo and return results.

    Args:
        query: String or list of strings to search for
        max_urls: Maximum number of URLs to return per query (default: 10)
        unique: Whether to filter out duplicate URLs (default: True)
        advanced: If True, return SearchResult objects with title and description.
                 If False, return only URLs. (default: False)

    Returns:
        If query is a string: List of URLs or SearchResult objects
        If query is a list: List of lists, each containing URLs or SearchResult objects
    """
    if isinstance(query, str):
        return _handle_single_query(query=query, max_urls=max_urls, unique=unique, advanced=advanced)

    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(
            lambda q: _handle_single_query(q, max_urls, unique, advanced),
            query
        ))

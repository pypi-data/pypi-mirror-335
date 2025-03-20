import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import field
from multiprocessing import cpu_count
from urllib.parse import quote_plus
from typing import List
import time

from bs4 import BeautifulSoup
from pydantic import BaseModel
from playwright.sync_api import sync_playwright


class SearchResult(BaseModel):
    query: str
    urls: list = field(default_factory=list)
    search_provider: str = ""
    page_source: str = ""


class OptimizedMultiQuerySearcher:
    def __init__(self, max_workers=None, animation=False):
        self.max_workers = max_workers or min(32, cpu_count() - 2)
        self.animation = animation
        self.params = {
            "bing": {"search": "b_results"},
            "google": {"search": "search"}
        }

    def _setup_browser(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=not self.animation
        )
        return playwright, browser

    def search_single_query(self, query, search_provider="google", min_waiting_time: int = 2):
        playwright, browser = self._setup_browser()
        try:
            page = browser.new_page()
            encoded_query = quote_plus(query)
            search_url = f"https://www.{search_provider}.com/search?q={encoded_query}"

            page.goto(search_url)
            time.sleep(min_waiting_time)

            # Wait for results
            page.wait_for_selector(f"#{self.params[search_provider]['search']}")

            soup = BeautifulSoup(page.content(), 'html.parser')
            atags = soup.find_all('a', attrs={'href': re.compile("^https://")})

            urls = self.extract_urls(atags)

            return SearchResult(
                query=query,
                urls=urls,
                search_provider=search_provider,
                page_source=page.content()
            )
        except Exception as e:
            print(f'exception as {e}')
            return SearchResult(query=query)
        finally:
            browser.close()
            playwright.stop()

    async def search_multiple_queries(self, queries: List[str], num_results=10,
                                      search_provider=None, return_only_urls=False,
                                      min_waiting_time: int = 2) -> List[SearchResult]:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            providers_list = self.params.keys() if search_provider is None else [search_provider]
            tasks = [
                loop.run_in_executor(
                    executor,
                    self.search_single_query,
                    query,
                    provider,
                    min_waiting_time
                )
                for query in queries for provider in providers_list
            ]
            result = await asyncio.gather(*tasks)
            if return_only_urls:
                all_urls = [url.urls for url in result]
                filtered_urls = [y for x in zip(*all_urls) for y in x]
                return filtered_urls
            return result

    def extract_urls(self, atags):
        all_urls = [u.get("href") for u in atags if u.get("href")]

        filtered_urls = [url for url in all_urls if 'google' not in url]

        yt_urls = []
        non_yt_urls = []
        for url in filtered_urls:
            if 'youtube' in url:
                yt_urls.append(url)
            else:
                non_yt_urls.append(url)

        return non_yt_urls + yt_urls


class RealTimeGoogleSearchProvider:
    def __init__(self, search_provider="google", max_workers=None, animation=False):
        self.search_provider = search_provider
        self.max_workers = max_workers
        self.animation = animation

    def search(self, query: str, max_urls=50, min_waiting_time: int = 2) -> List[str]:
        with OptimizedMultiQuerySearcher(max_workers=self.max_workers,
                                         animation=self.animation) as searcher:
            res = searcher.search_single_query(
                query,
                search_provider=self.search_provider,
                min_waiting_time=min_waiting_time
            )
            return res.urls[:max_urls]

    async def _async_batch_search(self, batch_queries, max_urls=50) -> List[str]:
        with OptimizedMultiQuerySearcher(max_workers=self.max_workers,
                                         animation=self.animation) as searcher:
            all_urls = await searcher.search_multiple_queries(
                queries=batch_queries,
                search_provider=self.search_provider
            )
            all_urls = [url.urls for url in all_urls]
            filtered_urls = [y for x in zip(*all_urls) for y in x]
            filtered_urls = [self._extract_until_hash(x) if self._is_hash(x) else x for x in filtered_urls]
            filtered_urls = [_ for _ in filtered_urls if _]
            return self._remove_duplicate_urls(filtered_urls)[:max_urls]

    def search_batch(self, batch_queries, max_urls=50) -> List[str]:
        return asyncio.run(self._async_batch_search(batch_queries, max_urls=max_urls))

    def __call__(self, query: str | list, *args, **kwargs):
        if isinstance(query, str):
            return self.search(query, *args, **kwargs)
        return self.search_batch(query, *args, **kwargs)

    def _is_hash(self, x):
        return '#' in x

    def _extract_until_hash(self, x):
        results = re.findall(r'(.*)#', x)
        return results[0] if results else ""

    def _remove_duplicate_urls(self, filtered_urls):
        seen = set()
        seen_add = seen.add
        return [x for x in filtered_urls if not (x in seen or seen_add(x))]
from concurrent.futures.thread import ThreadPoolExecutor

from googlesearch import search, SearchResult


def _handle_single_query(query, max_urls=10, unique=True, advanced=False):
    urls = list(search(query, num_results=max_urls, unique=unique,advanced=advanced))
    if advanced:
        https_urls = [res for res in urls if 'http' == res.url[:4]]
    else:
        https_urls = [url for url in urls if 'http' == url[:4]]
    return https_urls
def google(query: str|list, max_urls=10, unique=True, advanced=False) -> list[str]|list[SearchResult]:
    if isinstance(query,str):
        return _handle_single_query(query=query,max_urls=max_urls,unique=unique,advanced=advanced)
    with ThreadPoolExecutor(max_workers=4) as executors:
        return list(executors.map(_handle_single_query,query))

if __name__ == '__main__':
    res = google("who is modi", max_urls=2, advanced=True)
    for r in res:
        print(r.url)
        print(r.title)
        print(r.description)

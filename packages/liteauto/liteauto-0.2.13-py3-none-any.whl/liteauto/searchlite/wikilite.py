from concurrent.futures import ThreadPoolExecutor
import wikipedia as original_wiki
from typing import Union, List, Dict


def wikipedia(query: list | str, results: int = 10, lang: str = 'en') -> Dict[str, Union[str, List[str]]] | List[
    Dict[str, Union[str, List[str]]]]:
    """
    Search Wikipedia using direct API features.

    Args:
        query (str): Search query
        results (int): Number of results to return (default: 10)
        lang (str): Language code (default: 'en')

    Returns:
        Dict containing search results and suggestions
    """
    # Set language

    if isinstance(query, list):
        return wiki_batch_search(queries=query, results=results, lang=lang)

    original_wiki.set_lang(lang)

    try:
        # Get search results
        search_results = original_wiki.search(query, results=results)

        # Get summary of first result if available
        if search_results:
            try:
                page = original_wiki.page(search_results[0], auto_suggest=False)
                main_summary = page.summary
                main_url = page.url
                main_title = page.title

                # Get references and images
                references = page.references
                images = page.images

                # Get suggestions for related pages
                suggestions = original_wiki.search(f"{query} related", results=5)

            except original_wiki.DisambiguationError as e:
                # Handle disambiguation pages
                main_summary = f"Multiple matches found: {', '.join(e.options[:5])}"
                main_url = ""
                main_title = query
                references = []
                images = []
                suggestions = e.options[:5]

            except original_wiki.PageError:
                # Handle non-existent pages
                main_summary = "No exact matches found"
                main_url = ""
                main_title = query
                references = []
                images = []
                suggestions = search_results[1:6] if len(search_results) > 1 else []
        else:
            main_summary = "No results found"
            main_url = ""
            main_title = query
            references = []
            images = []
            suggestions = []

        return {
            'title': main_title,
            'summary': main_summary,
            'url': main_url,
            'search_results': search_results,
            'suggestions': suggestions,
            'references': references[:5],  # Limit to first 5 references
            'images': images[:5],  # Limit to first 5 images
            'language': lang
        }

    except Exception as e:
        return {
            'title': query,
            'summary': f"Error occurred: {str(e)}",
            'url': '',
            'search_results': [],
            'suggestions': [],
            'references': [],
            'images': [],
            'language': lang
        }


def wiki_batch_search(queries: List[str], results: int = 10, lang: str = 'en') -> List[
    Dict[str, Union[str, List[str]]]]:
    """
    Perform batch Wikipedia searches.

    Args:
        queries (List[str]): List of search queries
        results (int): Number of results per query (default: 10)
        lang (str): Language code (default: 'en')

    Returns:
        List of dictionaries containing search results
    """
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(
            lambda q: wiki_search(q, results, lang),
            queries
        ))


if __name__ == '__main__':
    # Single search example
    result = wiki_search("Python programming")
    print("\nSingle Search Result:")
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Summary: {result['summary'][:200]}...")
    print(f"Suggestions: {', '.join(result['suggestions'])}")

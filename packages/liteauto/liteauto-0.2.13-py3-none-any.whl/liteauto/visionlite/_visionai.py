from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from typing import List, Optional
import time

import pandas as pd
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from ..searchlite import google
from ..parselite import parse, FastParserResult
from wordllama import WordLlama
import datetime
from ..search_gen._search_gen import SearchGen



_loaded_llm = None


def get_llm():
    global _loaded_llm
    if _loaded_llm is None:
        _loaded_llm = WordLlama.load()
    return _loaded_llm


def get_topk(llm=None, query=None, contents=None, k=None):
    try:
        return llm.topk(query, llm.split("".join(contents)), k=k)
    except:
        return []


def get_parsed_result(urls=None, allow_pdf_extraction=False, allow_youtube_urls_extraction=False):
    parser_results: List[FastParserResult] = parse(urls, allow_pdf_extraction=allow_pdf_extraction,
                                                   allow_youtube_urls_extraction=allow_youtube_urls_extraction)
    parser_results_v1 = [_ for _ in parser_results if _.content]
    return parser_results_v1


@dataclass
class MultiQuerySearchResult:
    query: str
    results: List[FastParserResult]


def multi_extract_url_and_contents(query, max_urls):
    list_of_list_of_urls = google(query=query, max_urls=max_urls)
    parsed_list_of_list_of_urls = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        parsed_list_of_list_of_urls.extend(list(executor.map(get_parsed_result, list_of_list_of_urls)))

    final = [MultiQuerySearchResult(query=q, results=res) for q, res in zip(query, parsed_list_of_list_of_urls)]
    return final


def get_fastparser_result(query=None, animation=None, allow_pdf_extraction=None, allow_youtube_urls_extraction=None):
    urls: List[str] = google(query, animation=animation)
    parser_results_v1 = get_parsed_result(urls, allow_pdf_extraction, allow_youtube_urls_extraction)
    return parser_results_v1


def get_relevant_chunks(query, contents: list,
                        k=None, split_targe_size: int = 1000, llm=None):
    final_results = []
    for result in contents:
        contents = llm.split(result.content, target_size=split_targe_size)
        topk = llm.topk(query=query, candidates=contents, k=k)
        final_results.extend([{"url": result.url, "query": query,
                               "chunk": c} for c in topk])
    return final_results


def create_dataframe_from_results(multiquery_results):
    df = pd.DataFrame([{"query": x.query,
                        "url": y.url,
                        "content": y.content} for x in multiquery_results for y in x.results])
    return df


def get_topk_chunk_and_url(df):
    newdf = df.explode('top_k').reset_index(drop=True)
    df2 = newdf.groupby('top_k')['url'].first().reset_index()
    return df2


def vision_version1(query, k=3, max_urls=5, animation=False,
                    allow_pdf_extraction=True,
                    allow_youtube_urls_extraction=False,
                    embed_model=None, genai_query_k=3, model="llama3.2:1b-instruct-q4_K_M",
                    base_url="http://localhost:11434",
                    temperature=0.1, max_retries=3,
                    api_key="", llm=None):
    urls = google(query, max_urls=max_urls, animation=animation)
    contents = parse(urls, allow_pdf_extraction=allow_pdf_extraction,
                     allow_youtube_urls_extraction=allow_youtube_urls_extraction)
    contents = [c.content for c in contents]

    if len(contents) == 0:
        return f"Urls:\n{urls}"

    llm = embed_model or get_llm()

    queries = SearchGen(model=model,
                        temperature=temperature,
                        max_retries=max_retries,
                        base_url=base_url
                        , api_key=api_key)(query, genai_query_k)
    vars = []
    for query in queries:
        ans = get_topk(
            llm=llm,
            query=query,
            contents=contents,
            k=k
        )
        vars.extend(ans)
    res = list(set(vars))

    if len(res) <= 3:
        topk: List[str] = res
    else:
        topk: List[str] = llm.topk(query=query, candidates=res, k=k) if len(res)>k else res

    updated_res = "\n### Results:  \n" + "  \n".join(topk) + "  \n\n### URLs:  \n" + "  \n".join(urls)

    return updated_res


def visionai(query,
             max_urls=5,
             k=3,
             model="llama3.2:1b-instruct-q4_K_M",
             base_url="http://localhost:11434",
             temperature=0.1,
             max_retries=5,
             animation=False,
             allow_pdf_extraction=True,
             allow_youtube_urls_extraction=False,
             embed_model=None,
             genai_query_k: int | None = 5,
             query_k: int | None = 5,
             return_type="str",
             api_key="",
             llm=None):
    gen_queries = SearchGen(
        model=model,
        temperature=temperature,
        max_retries=max_retries,
        base_url=base_url,
        api_key=api_key,
        llm=llm
    )
    queries = gen_queries(query, query_k)
    if not queries:
        return ["Failed to generate search queries"] if return_type == "list" else "Failed to generate search queries"

    vision_with_args = partial(
        vision_version1,
        k=k,
        max_urls=max_urls,
        animation=animation,
        allow_pdf_extraction=allow_pdf_extraction,
        allow_youtube_urls_extraction=allow_youtube_urls_extraction,
        embed_model=embed_model,
        genai_query_k=genai_query_k,
        temperature=temperature,
        model=model,
        max_retries=max_retries,
        base_url=base_url,
        llm=llm
    )

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(vision_with_args, queries))
        results = list(set(results))

    if return_type == "list":
        return results
    else:
        result_str = "## ".join(results)
        return result_str


def minivisionai(query,
                 max_urls=5,
                 k=5,
                 model="llama3.2:1b-instruct-q4_K_M",
                 base_url="http://localhost:11434",
                 temperature=0.1,
                 max_retries=3,
                 animation=False,
                 allow_pdf_extraction=True,
                 allow_youtube_urls_extraction=False,
                 embed_model=None,
                 genai_query_k: int | None = 3,
                 query_k: int | None = 5,
                 return_type="str",
                 api_key=""):
    return visionai(query, max_urls=max_urls, k=k, model=model, base_url=base_url, temperature=temperature,
                    max_retries=max_retries, animation=animation, allow_pdf_extraction=allow_pdf_extraction,
                    allow_youtube_urls_extraction=allow_youtube_urls_extraction, embed_model=embed_model,
                    genai_query_k=genai_query_k, query_k=query_k, return_type=return_type,
                    api_key=api_key)


def deepvisionai(query,
                 max_urls=15,
                 k=10,
                 model="llama3.2:1b-instruct-q4_K_M",
                 base_url="http://localhost:11434",
                 temperature=0.05,
                 max_retries=10,
                 animation=False,
                 allow_pdf_extraction=True,
                 allow_youtube_urls_extraction=False,
                 embed_model=None,
                 genai_query_k: int | None = 7,
                 query_k: int | None = 15,
                 return_type="str",
                 api_key=""):
    return visionai(query, max_urls=max_urls, k=k, model=model, base_url=base_url, temperature=temperature,
                    max_retries=max_retries, animation=animation, allow_pdf_extraction=allow_pdf_extraction,
                    allow_youtube_urls_extraction=allow_youtube_urls_extraction, embed_model=embed_model,
                    genai_query_k=genai_query_k, query_k=query_k, return_type=return_type,
                    api_key=api_key)


def main():
    queries = [
        # 'what are the new features introduced in latest crewai framework',
        # 'how does the crewai framework improve performance',
        # 'can you explain the architecture of crewai framework',
        # 'what are the use cases for crewai framework',
        # 'how does crewai framework handle data privacy',
        # 'what are the system requirements for crewai framework',
        # 'can crewai framework be integrated with other tools',
        # 'what are the licensing terms for crewai framework',
        # 'how can I get support for crewai framework',
        'are there any tutorials or documentation available for crewai framework'
    ]

    for query in queries:
        r = visionai(query, base_url="http://192.168.170.76:11434")
        print(r)


if __name__ == "__main__":
    main()

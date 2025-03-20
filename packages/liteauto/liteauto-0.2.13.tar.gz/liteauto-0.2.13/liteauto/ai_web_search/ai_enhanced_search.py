import concurrent.futures
import itertools
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple

from litegen import genai

from liteauto.parselite import parse
from liteauto.searchlite import google
from liteauto.visionlite import wlanswer, wlsimchunks, wlsplit, wltopk
from liteutils import remove_references


@dataclass
class GoogleSearchDocument:
    url: str
    content: str


class GoogleSearch:
    @classmethod
    def get_urls_from_google_search(cls,query,max_urls=5):
        urls = google(query, max_urls=max_urls)
        return urls
    @classmethod
    def get_search_documents_from_google(cls, query) -> List[GoogleSearchDocument]:
        urls: List = GoogleSearch.get_urls_from_google_search(query)
        contents = parse(urls,llm=False)
        return [GoogleSearchDocument(url=r.url, content=r.content) for r in contents if r.content]

    @classmethod
    def get_multi_urls_parsed_documents(cls, urls: List[List]) -> List[GoogleSearchDocument]:
        results: List = []
        for url in urls:
            parsed_data = parse(url,llm=False)
            results.extend(parsed_data)
        results = [GoogleSearchDocument(url=r.url, content=r.content) for r in results if r.content]
        return results

    @classmethod
    def get_relevant_chunk_from_text_corpus(cls, query: str, text: str, k=2) -> str:
        query = GoogleSearch.filter_query(query)
        return wlanswer(context=text, query=query, k=k)

    @classmethod
    def get_relevant_chunks_multiple_topk(cls, query: str, text: str, k=5):
        query = GoogleSearch.filter_query(query)
        return wlsimchunks(context=text, query=query, k=k)

    @classmethod
    def get_ai_generated_search_queries(cls, prompts: List[str]) -> List[str]:
        _SYSTEM_PROMPT = """You are google search query generator, based on user query and context,
            generate a single ONE search query that one of the best way to search for better google results.

            Format your response as;
            [SEARCH_QUERY]: Your answer here .

            Generate directly question

            Example:
            <context>mahatma gandhi born on october 2dn ... some more information</context>
            <query>who is mother of mahatman gandhi?</query>
            [SEARCH_QUERY]: Gandhi's mother name?

            <context>the capital of france is paris and it is beautiful place ...</context>
            <query>what is the capital of france?</query>
            [SEARCH_QUERY]: france has a capital?

            ...
            """

        def run_genai(prompt):
            res = genai(system_prompt=_SYSTEM_PROMPT, prompt=prompt, temperature=0.7)
            return res.split(":")[-1].strip().replace('"', "").replace("'", "").lower()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            result = list(executor.map(run_genai, prompts))
        return list(set(result))

    @classmethod
    def prepare_prompt_for_google_queries_generation(cls, pair_of_qc: List[Tuple[str, str]]) -> List[str]:
        pair_of_qc = [(q,remove_references(c)) for q,c in pair_of_qc] ## for Research papers
        _USER_PROMPT = """<context>{context}</context>
            <query>{query}</query>
            [SEARCH_QUERY]:"""
        return [_USER_PROMPT.format(context=context, query=query) for query, context in pair_of_qc]

    @classmethod
    def filter_query(cls,query:str):
        replace_with_empty = [
            "arxiv",
            "research",
            "pdf",
            "preprint",
            "review",
            "published",
            "published in",
            "paper"
            "papers"
        ]
        for word in replace_with_empty:
            query = query.replace(word, "")

        return query

    @classmethod
    def generate_search_queries(cls, input_query, doc_k=5) -> List[str]:
        google_docs: List[GoogleSearchDocument] = GoogleSearch.get_search_documents_from_google(input_query)

        relevant_chunks: List[List] = [GoogleSearch.get_relevant_chunks_multiple_topk(query=input_query,
                                                                                      text=g.content,
                                                                                      k=doc_k)
                                       for g in google_docs]

        relevant_chunks: List[str] = list(itertools.chain.from_iterable(relevant_chunks))

        qc_pairs: List[Tuple[str, str]] = [(input_query, c) for c in relevant_chunks]

        prompts = GoogleSearch.prepare_prompt_for_google_queries_generation(qc_pairs)

        search_queries: List[str] = GoogleSearch.get_ai_generated_search_queries(prompts)
        return search_queries

    @classmethod
    def perform_search_and_get_topk_chunk_answer(cls, query) -> List[GoogleSearchDocument]:
        google_docs: List[GoogleSearchDocument] = GoogleSearch.get_search_documents_from_google(query)
        google_top_chunk_filtered = [GoogleSearchDocument(url=doc.url,
                                                          content=GoogleSearch.get_relevant_chunk_from_text_corpus(
                                                              query=query,
                                                              text=doc.content
                                                          )) for doc in google_docs]
        return google_top_chunk_filtered

    @classmethod
    def perform_multi_queries_search(cls, input_query:str,doc_k=5) -> List[GoogleSearchDocument]:
        queries = GoogleSearch.generate_search_queries(input_query,doc_k=doc_k)
        urls:List[List] = GoogleSearch.get_urls_from_google_search(queries)
        google_docs: List[GoogleSearchDocument] = GoogleSearch.get_multi_urls_parsed_documents(urls)
        google_top_chunk_filtered = [GoogleSearchDocument(url=doc.url,
                                                          content=GoogleSearch.get_relevant_chunk_from_text_corpus(
                                                              query=input_query,
                                                              text=doc.content
                                                          )) for doc in google_docs]
        final_docs = defaultdict(list)
        for i, doc in enumerate(google_top_chunk_filtered):
            final_docs[doc.url].append(doc.content)

        final_docs = [GoogleSearchDocument(url=u,content="".join(list(set(c)))) for u,c in final_docs.items()]
        return final_docs


if __name__ == '__main__':
    import os

    os.environ['OPENAI_MODEL_NAME'] = "qwen2.5:7b-instruct"
    os.environ['OPENAI_API_KEY'] = "dsollama"

    input_query = "how ai agents learn in the environment"
    results:List[GoogleSearchDocument] = GoogleSearch.perform_multi_queries_search(input_query)
    for a in results:
        print(f'Source: {a.url}\n\n Content:\n{a.content}')
        print('-'*50)

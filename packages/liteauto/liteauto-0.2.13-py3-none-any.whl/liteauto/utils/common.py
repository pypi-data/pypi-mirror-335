from concurrent.futures import ThreadPoolExecutor

from liteutils import read_arxiv

from liteauto.searchlite import google
from liteauto.parselite import parse
from liteauto.visionlite import wlanswer,wlsplit
from litegen import LLM


def web(
    query: str,
    max_urls: int = 1,
):
    """
    Fetches and parses web content based on a query.

    Args:
        query (str): The search query to fetch web content for.
        max_urls (int): The maximum number of URLs to fetch content from. Defaults to 1.

    Returns:
        str: A string containing the parsed content from the fetched web pages.
    """
    docs = parse(google(query, max_urls=max_urls))
    context = "\n".join([d.content for d in docs if d.content])
    return context


def web_top_chunk(
    query: str,
    retreive_query: str = None,
    max_urls: int = 1,
    k: int | None = None
):
    docs = parse(google(query, max_urls=max_urls))
    context = "\n".join([d.content for d in docs if d.content])
    if retreive_query:
        return wlanswer(context, retreive_query or query, k=k or 1)
    if k:
        return wlanswer(context,retreive_query or query, k=k)

    return context

def compress_sequential(text, additional_prompt="",n=1):
    genai = LLM()
    if n==0:
        return text
    chunks = wlsplit(text)
    res = ""
    for c in chunks:
        res += genai(
            prompt=
            # f"compress and have simple explanation in english with core details to takeaway, "
            #                 f"note: keep python codes exactly same,"
            #                 f"for normal like 100 to 10 words ration compression: [CONTENT]\n {c}"
                   f"compress and have simple explanation in english with core details to takeaway, like 100 to 10 words ration compression: [CONTENT]\n {c}"
        )+"\n"
    return compress_sequential(text,additional_prompt,n-1)


def compress(text, additional_prompt="",n=1,llm=None):
    llm = llm or LLM()
    if n==0:
        return text
    chunks = wlsplit(text)
    def generate(c):
        # return genai(prompt=f"compress and have simple explanation in english with core details to takeaway,"
        #                     f"note: keep python codes exactly same\n {additional_prompt}"
        #                     f"for normal like 100 to 10 words ration compression: [CONTENT]\n {c}")+"\n"
        return llm(prompt=f"compress and have simple explanation in english with core details to takeaway, like 100 to 10 words ration compression: [CONTENT]\n {c}")+"\n"

    with ThreadPoolExecutor(max_workers=4) as executor:
        res = "\n".join(list(executor.map(generate,chunks)))
    return compress(res,additional_prompt,n-1,llm=llm)

def summary(query:str,max_urls=1,compress_turns=1,k:int|None=None):
    return compress(web(query,max_urls=max_urls,k=k),n=compress_turns)

def get_summaries(df):
    df['basic'] = ''
    df['summary'] = ''
    df['keypoints'] = ''
    df['tweet'] = ''
    for i,d in df.iterrows():
        basic = compress(read_arxiv(d['pdf_url']))
        summary = compress(basic)
        keypoints = compress(summary)
        tweet = compress(keypoints)
        # Update the DataFrame with the new values
        df.at[i, 'simplified'] = basic
        df.at[i, 'summary'] = summary
        df.at[i, 'keypoints'] = keypoints
        df.at[i, 'tweet'] = tweet
    return df

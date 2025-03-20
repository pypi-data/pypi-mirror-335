import asyncio
import aiohttp
import PyPDF2
import fitz
import trafilatura
import ssl
import certifi

from dataclasses import dataclass
from io import BytesIO
from tqdm import tqdm
from typing import List, Tuple

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


@dataclass
class FastParserResult:
    url: str
    content: str


class YoutubeExtractor:
    @staticmethod
    def get_video_id(url):
        return url.split("?v=")[-1]

    @staticmethod
    def extract(urls: list):
        urls = [YoutubeExtractor.get_video_id(url) for url in urls]
        results = []
        formatter = TextFormatter()
        for url in urls:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(url)
                transcript = formatter.format_transcript(transcript)
                results.append(transcript)
            except:
                pass
        return results


class FastHTMLParserV3:
    def __init__(self):
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def _fetch_url(self, session, url, url_fetch_timeout=10):
        if self._is_avoid_urls(url):
            return ""
        try:
            async with session.get(url, timeout=url_fetch_timeout, ssl=self.ssl_context) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._process_trafili_html(html)
                else:
                    return ""
        except aiohttp.ClientConnectorError as e:
            print(f"Connection error for {url}: {str(e)}")
            return ""
        except asyncio.TimeoutError:
            print(f"Timeout error for {url}")
            return ""
        except aiohttp.ClientConnectorCertificateError as e:
            print(f"SSL Certificate error for {url}: {str(e)}")
            return ""
        except Exception as e:
            print(f"Unexpected error fetching {url}: {str(e)}")
            return ""

    async def fetch_content(self, urls, url_fetch_timeout=10):
        conn = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = [self._fetch_url(session, url, url_fetch_timeout) for url in urls]
            return await asyncio.gather(*tasks)

    def _is_avoid_urls(self, url):
        if "https://arxiv.org/pdf" in url.lower() or url.endswith(".pdf") or "youtube.com/watch" in url.lower():
            return True
        return False

    def _process_trafili_html(self, html):
        text = trafilatura.extract(html, include_formatting=True)
        return text


class FastParser:
    def __init__(self, extract_pdf=True,
                 allow_youtube_urls_extraction=False,
                 only_abstract=False,
                 llm=True):
        self.llm = llm
        self.extract_pdf = extract_pdf
        self.allow_youtube_urls_extraction = allow_youtube_urls_extraction
        self.only_abstract = only_abstract
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    def fetch(self, url: str):
        res = self.fetch_batch([url])
        return FastParserResult(url=url, content=res[0].content if res else "")

    def fetch_batch(self, urls: list) -> List[FastParserResult]:
        return asyncio.run(self._async_html_parser(urls))

    async def afetch_batch(self, urls: list) -> List[FastParserResult]:
        return await self._async_html_parser(urls)

    async def afetch(self, url: str):
        res = await self.afetch_batch([url])
        return FastParserResult(url=url, content=res[0][1] if res else "")

    async def aparse(self, urls: str | list, *args, **kwargs) -> FastParserResult | List[FastParserResult]:
        if isinstance(urls, str):
            return await self.afetch(urls)
        return await self.afetch_batch(urls)

    def __call__(self, urls: str | list, *args, **kwargs) -> FastParserResult | List[FastParserResult]:
        if isinstance(urls, str):
            return self.fetch(urls)
        return self.fetch_batch(urls)

    async def _async_html_parser(self, urls) -> List[FastParserResult]:
        html_urls = []
        pdf_urls = []
        yt_urls = []
        for url in urls:
            url = self._arxiv_url_fix(url)
            url = self._handle_abs_url(url)
            if '/pdf' in url or url.lower().endswith('.pdf'):
                pdf_urls.append(url)
            elif 'youtube' in url:
                yt_urls.append(url)
            else:
                html_urls.append(url)

        results: List = []

        html_urls = list(dict.fromkeys(html_urls))
        pdf_urls = list(dict.fromkeys(pdf_urls))
        yt_urls = list(dict.fromkeys(yt_urls))

        # print(f'{html_urls=}')
        # print(f'{pdf_urls=}')
        # print(f'{yt_urls=}')

        if html_urls:
            fetcher = FastHTMLParserV3()
            html_results = await fetcher.fetch_content(urls=html_urls)
            results.extend(list(zip(html_urls, html_results)))

        if pdf_urls and self.extract_pdf:
            pdf_results = await self._fetch_pdf_content(pdf_urls)
            results.extend(list(zip(pdf_urls, pdf_results)))

        if self.allow_youtube_urls_extraction:
            yt_results = YoutubeExtractor.extract(urls=yt_urls)
            results.extend(list(zip(yt_urls, yt_results)))

        result_v1 = [FastParserResult(url=u, content=c) for u, c in results]
        return result_v1

    async def _fetch_pdf_content(self, pdf_urls):
        async def fetch_pdf(session, url):
            async with session.get(url, ssl=self.ssl_context) as response:
                if response.status == 200:
                    pdf_bytes = await response.read()
                    if self.llm:
                        return self.pymupdfllm_process(pdf_bytes)
                    else:
                        return self.pymupdf_process(pdf_bytes)
                else:
                    return ""

        conn = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=conn) as session:
            tasks = [fetch_pdf(session, url) for url in pdf_urls]
            results = await asyncio.gather(*tasks)
            return results

    def _arxiv_url_fix(self, url):
        if 'https://arxiv.org/abs/' in url and self.extract_pdf:
            return url.replace('https://arxiv.org/abs/', 'https://arxiv.org/pdf/')
        elif 'http://arxiv.org/html/' in url:
            if self.only_abstract:
                return url.replace('http://arxiv.org/html/', 'https://arxiv.org/abs/')
            else:
                return url.replace('http://arxiv.org/html/', 'https://arxiv.org/pdf/')
        else:
            return url

    def pymupdf_process(self, pdf_bytes):
        pdf_file = BytesIO(pdf_bytes)
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text

    def pymupdfllm_process(self, pdf_bytes):
        import pymupdf4llm
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_path = temp_pdf.name

        try:
            md_text = pymupdf4llm.to_markdown(temp_path)
            return md_text
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _handle_abs_url(self, url):
        if self.only_abstract:
            return url.replace("/pdf","/abs").replace("/html","/abs")
        return url


def parse(urls: list | str, allow_pdf_extraction=True,
          allow_youtube_urls_extraction=False, only_abstract=False, llm=False) -> List[FastParserResult] | FastParserResult:
    """takes urls and parse and returns pydantic model of Response(url:str, content:str|None)"""
    parser = FastParser(extract_pdf=allow_pdf_extraction,
                        allow_youtube_urls_extraction=allow_youtube_urls_extraction,
                        only_abstract=only_abstract,
                        llm=llm)
    return parser(urls)


async def aparse(urls: list | str, allow_pdf_extraction=True,
                 allow_youtube_urls_extraction=False, only_abstract=False, llm=False) -> List[FastParserResult] | FastParserResult:
    parser = FastParser(extract_pdf=allow_pdf_extraction,
                        allow_youtube_urls_extraction=allow_youtube_urls_extraction,
                        only_abstract=only_abstract,
                        llm=llm)
    return await parser.aparse(urls)
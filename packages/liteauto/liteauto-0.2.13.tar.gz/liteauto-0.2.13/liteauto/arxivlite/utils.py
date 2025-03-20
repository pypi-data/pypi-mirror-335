import itertools
import os
import re
from typing import List

import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from tqdm import tqdm

from .const import BASE_URL
from .schema import Paper, ArxivTags


def download_html(urls: List[str]) -> List[str]:
    """Using multithreading download and return result"""

    def fetch_url(url: str) -> str:
        response = requests.get(url)
        return response.text

    with ThreadPoolExecutor() as executor:
        return list(executor.map(fetch_url, urls))


def build_urls_from_tag(tags):
    return [BASE_URL.format(tag=f"cs.{t}") for t in tags.to_dict().keys()]


def parse_arxiv_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    papers = []

    # Find all dt and dd pairs (each paper entry)
    dts = soup.find_all('dt')
    dds = soup.find_all('dd')

    for dt, dd in zip(dts, dds):
        paper = {}

        # Extract title
        title_div = dd.find('div', class_='list-title')
        if title_div:
            # Remove "Title:" text and clean up whitespace
            title = title_div.text.replace('Title:', '').strip()
            paper['title'] = title

        # Extract PDF ID
        pdf_link = dt.find('a', id=re.compile('^pdf-'))
        if pdf_link:
            paper['pdf_id'] = pdf_link['id'].replace('pdf-', '')

        # Extract subjects
        subjects_div = dd.find('div', class_='list-subjects')
        if subjects_div:
            # Get main subject (primary-subject)
            primary_subject = subjects_div.find('span', class_='primary-subject')
            if primary_subject:
                paper['main_subject'] = primary_subject.text.strip()

            # Get all subjects
            all_subjects = subjects_div.text.replace('Subjects:', '').strip()
            paper['all_subjects'] = [s.strip() for s in all_subjects.split(';')]

        papers.append(
            Paper(
                title=paper.get('title', ""),
                tag=paper.get('main_subject', ""),
                all_tags=paper.get('all_subjects', []),
                pdf_id=paper.get("pdf_id", "")
            )
        )

    return papers


def multiprocessing_parse_arxiv_html(data) -> list[Paper]:
    with ThreadPoolExecutor() as executor:
        results: list[list[Paper]] = list(executor.map(parse_arxiv_html, data))

    results: list[Paper] = list(itertools.chain.from_iterable(results))
    return results


def post_process_deduplication(results: list):
    df = pd.DataFrame([r.to_dict() for r in results])

    df_no_duplicates = df.drop_duplicates(subset=['pdf_id'], keep='first')

    tags = [f'cs.{x}' for x in ArxivTags().to_dict().keys()]

    def extract_tag_code(tag_string):
        # Example: converts "Machine Learning (cs.LG)" to "cs.LG"
        if '(' in tag_string:
            return tag_string.split('(')[1].rstrip(')')
        return tag_string

    df_filtered = df_no_duplicates[df_no_duplicates['tag'].apply(extract_tag_code).isin(tags)].copy()
    return df_filtered

def dump_data(df, dir='data'):
    from liteutils import read_arxiv
    os.makedirs(dir, exist_ok=True)

    urls = df['pdf_url'].tolist()
    ids = df['pdf_id'].tolist()

    for i, r in tqdm(zip(ids, urls), desc="extracting url ...", total=len(urls)):
        text = read_arxiv(r)
        with open(f'{dir}/{i}.txt', "w") as f:
            f.write(text)
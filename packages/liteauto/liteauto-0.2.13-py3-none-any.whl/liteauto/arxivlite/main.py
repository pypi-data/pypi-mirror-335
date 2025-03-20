from pandas import DataFrame
from urllib3 import Retry

from .schema import ArxivTags,Paper
from .utils import (build_urls_from_tag,
                    download_html,
                    multiprocessing_parse_arxiv_html,
                    post_process_deduplication)


import ast

import pandas as pd
from pandas import DataFrame

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter
import ast
import os
from wordcloud import WordCloud
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time
import logging
from requests.adapters import HTTPAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("arxiv_processor.log"), logging.StreamHandler()]
)
logger = logging.getLogger("ArxivProcessor")


def get_todays_arxiv_papers() -> DataFrame:
    """return dataframe of todays reserach papers and its infromation release in arxiv website"""
    tags = ArxivTags()

    urls = build_urls_from_tag(tags)
    data = download_html(urls)
    results: list[Paper] = multiprocessing_parse_arxiv_html(data)

    df_filtered: DataFrame = post_process_deduplication(results)
    return df_filtered



class ArxivHandler:
    def get_ai_relevant(self, df):
        dicard_tags = [
            "math.",
            "finance",
            "physics",
            "geometry",
            "chemical",
            "operating",
            "cs.os",
            "symbolic",
            "cs.sc",
            "physic",
            "bio.",
            "cs.pl",
            "programming",
            "cs.si",
            "application",
            "eess.as",
            "speech",
            "harware",
            "energy",
            "automata",
            "cs.fl",
            'quantum',
            "physics",
            "biomolecules",
            "robotics",
            "cs.ro",
            "database",
            "algebra",
            "signal",
            "eess.sp",
            "sound",
            "cs.ds",
            "cs.pf",
            "security",
            "cs.cy",
            "crypto",
            "stat.",
            "eess.",
            "econ.",
            "science",
            "cs.dc",
            "cs.ne",
            "trading",
            "fin.",
            "cond-mat.",
            "cs.cv",
            "cs.ni",
            "cs.dl",
            "cs.hc",
            "nlin.cd"
        ]

        filtered_df = df[df['all_tags'].str.contains('|'.join(["cs."]), case=False, regex=True)]
        filtered_df = filtered_df[~filtered_df['all_tags'].str.contains('|'.join(dicard_tags), case=False, regex=True)]
        return filtered_df

    def handle_category(self, df):
        """
        Categorize research papers based on keyword matching in titles for AI/ML research.

        Designed for AI engineers and data scientists to easily filter relevant papers.

        Args:
            df (pandas.DataFrame): DataFrame containing paper information

        Returns:
            pandas.DataFrame: DataFrame with an additional 'category' column
        """
        result_df = df.copy()
        result_df['category'] = 'other'

        # Define categories with their respective keywords
        categories = {
            # Review/overview papers
            'survey': ['survey'],
            'review': ['review', 'overview'],
            'tutorial': ['tutorial', 'introduction', 'primer', 'guide'],

            # Evaluation papers
            'bench': ['benchmark', 'leaderboard'],
            'evaluation': ['evaluation', 'assessment', 'measuring', 'performance'],
            'comparison': ['comparison', 'comparative', 'versus', 'vs'],

            # Resources
            'dataset': ['dataset', 'corpus', 'data', 'database'],
            'tool': ['tool', 'toolkit', 'library', 'software', 'platform', 'package'],

            # Methodological papers
            'method': ['method', 'approach'],
            'framework': ['framework'],
            'model': ['model', 'modeling', 'neural'],
            'algorithm': ['algorithm', 'algorithmic'],
            'architecture': ['architecture'],
            'implementation': ['implementation', 'implementing'],
            'technique': ['technique'],
            'pipeline': ['pipeline'],

            # Improvement papers
            'optimization': ['optimization', 'optimizing', 'efficient', 'efficiency'],
            'improvement': ['improvement', 'improving', 'enhanced', 'enhancing', 'better'],
            'extension': ['extension', 'extending', 'augmentation'],
            'scaling': ['scaling', 'scale', 'large-scale', 'scalable'],

            # Problem-solving papers
            'solution': ['solution', 'solving'],
            'challenge': ['challenge', 'challenging', 'difficult', 'problem'],

            # Applied papers
            'application': ['application', 'applying', 'applied'],
            'case study': ['case study', 'case-study', 'real-world'],
            'deployment': ['deployment', 'production', 'industry'],

            # Analysis papers
            'analysis': ['analysis', 'analyzing', 'analytical'],
            'study': ['study', 'investigation', 'investigating'],
            'experiment': ['experiment', 'experimental', 'empirical'],
            'exploration': ['exploration', 'exploring', 'exploratory'],

            # Specialty areas
            'interpretability': ['interpretability', 'explainable', 'xai', 'explanation'],
            'uncertainty': ['uncertainty', 'confidence', 'probabilistic', 'bayesian'],
            'fairness': ['fairness', 'bias', 'ethical', 'ethics'],
            'robustness': ['robustness', 'robust', 'adversarial', 'defense'],
            'transfer': ['transfer', 'adaptation', 'domain adaptation', 'fine-tuning'],
            'multimodal': ['multimodal', 'multi-modal', 'cross-modal'],
            'generative': ['generative', 'generation', 'synthesis', 'synthetic'],
            'distributed': ['distributed', 'federated', 'decentralized'],
            'few-shot': ['few-shot', 'zero-shot', 'one-shot', 'meta-learning'],
            'representation': ['representation', 'embedding', 'feature'],
            'attention': ['attention', 'transformer', 'self-attention'],
            'causality': ['causality', 'causal', 'cause'],
            'reinforcement': ['reinforcement', 'rl', 'policy', 'reward'],
            'graph': ['graph', 'gnn', 'network'],
            'privacy': ['privacy', 'anonymity', 'secure', 'security'],
            'compression': ['compression', 'compressed', 'quantization', 'distillation'],
            'continual': ['continual', 'lifelong', 'incremental', 'online'],
            'foundation': ['foundation', 'foundational', 'base', 'baseline'],
            'pretraining': ['pretraining', 'pretrained', 'pre-trained', 'self-supervised']
        }

        # Apply categorization
        for category, keywords in categories.items():
            for keyword in keywords:
                mask = result_df['title'].str.contains(r'\b' + keyword + r'\b', case=False, regex=True)
                result_df.loc[mask & (result_df['category'] == 'other'), 'category'] = category

        return result_df

    def visualize_paper_insights(self, df, output_dir="paper_insights"):
        """
        Generate insightful visualizations for arxiv papers dataset

        Args:
            df (pandas.DataFrame): DataFrame containing paper information with categories
            output_dir (str): Directory to save visualization images
        """
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Set the style
        sns.set(style="whitegrid")
        plt.rcParams.update({'font.size': 11, 'figure.figsize': (12, 8)})

        # 1. Category Distribution
        plt.figure(figsize=(14, 8))
        category_counts = df['category'].value_counts()
        # Only show top 20 categories for clarity
        if len(category_counts) > 20:
            category_counts = category_counts.head(20)

        ax = sns.barplot(x=category_counts.values, y=category_counts.index)
        plt.title('Distribution of Paper Categories (Top 20)', fontsize=16)
        plt.xlabel('Number of Papers', fontsize=14)
        plt.ylabel('Category', fontsize=14)

        # Add count labels to the bars
        for i, v in enumerate(category_counts.values):
            ax.text(v + 0.5, i, str(v), va='center')

        plt.tight_layout()
        plt.savefig(f"{output_dir}/category_distribution.png", dpi=300)
        plt.close()

        # 2. Tags Analysis
        # Extract and analyze tags
        all_tags = []
        for tags_str in df['all_tags']:
            try:
                tags = ast.literal_eval(tags_str)
                all_tags.extend(tags)
            except:
                continue

        tag_counter = Counter(all_tags)
        top_tags = pd.DataFrame({
            'tag': list(dict(tag_counter.most_common(20)).keys()),
            'count': list(dict(tag_counter.most_common(20)).values())
        })

        plt.figure(figsize=(14, 8))
        ax = sns.barplot(x='count', y='tag', data=top_tags)
        plt.title('Most Common Tags in Papers (Top 20)', fontsize=16)
        plt.xlabel('Count', fontsize=14)
        plt.ylabel('Tag', fontsize=14)

        # Add count labels
        for i, v in enumerate(top_tags['count']):
            ax.text(v + 0.5, i, str(v), va='center')

        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_tags.png", dpi=300)
        plt.close()

        # 3. Category by Tag Heatmap
        # Only use top 10 categories and top 10 tags for readability
        top_categories = df['category'].value_counts().head(10).index.tolist()

        # Create a filtered dataframe with only top categories
        filtered_df = df[df['category'].isin(top_categories)]

        # Create a tag-category matrix for heatmap
        # First get top 10 tags
        top_tags_list = [tag for tag, _ in tag_counter.most_common(10)]

        # Initialize matrix with zeros
        heatmap_data = np.zeros((len(top_categories), len(top_tags_list)))

        # Fill the matrix
        for i, category in enumerate(top_categories):
            category_df = filtered_df[filtered_df['category'] == category]
            for j, tag in enumerate(top_tags_list):
                count = 0
                for tags_str in category_df['all_tags']:
                    try:
                        tags = ast.literal_eval(tags_str)
                        if tag in tags:
                            count += 1
                    except:
                        continue
                heatmap_data[i, j] = count

        plt.figure(figsize=(16, 10))
        ax = sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlGnBu",
                         xticklabels=top_tags_list, yticklabels=top_categories)
        plt.title('Relationship Between Categories and Tags', fontsize=16)
        plt.xlabel('Tags', fontsize=14)
        plt.ylabel('Categories', fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/category_tag_heatmap.png", dpi=300)
        plt.close()

        # 4. Word Cloud of Paper Titles
        text = " ".join(title for title in df['title'])
        wordcloud = WordCloud(width=800, height=500,
                              background_color='white',
                              max_words=100,
                              collocations=False,
                              contour_width=3).generate(text)

        plt.figure(figsize=(16, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title('Word Cloud of Paper Titles', fontsize=16)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/title_wordcloud.png", dpi=300)
        plt.close()

        # 5. Category Distribution Pie Chart
        plt.figure(figsize=(14, 14))
        # For pie chart, limit to top 10 categories plus "Other"
        top_cats = df['category'].value_counts().head(10)
        other_count = df['category'].value_counts()[10:].sum()
        pie_data = pd.concat([top_cats, pd.Series([other_count], index=['Other'])])

        plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%',
                startangle=90, shadow=True, explode=[0.05] * len(pie_data))
        plt.title('Share of Top 10 Categories in Papers', fontsize=16)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/category_pie.png", dpi=300)
        plt.close()

        # 6. Category and Subcategory Analysis
        # Extract primary categories from all_tags (e.g., cs.AI, cs.LG)
        primary_categories = []
        for tags_str in df['all_tags']:
            try:
                tags = ast.literal_eval(tags_str)
                primaries = [tag.split('.')[0] + '.' + tag.split('.')[1] if '.' in tag else tag for tag in tags]
                primary_categories.extend(primaries)
            except:
                continue

        primary_counter = Counter(primary_categories)
        top_primaries = pd.DataFrame({
            'primary_category': list(dict(primary_counter.most_common(15)).keys()),
            'count': list(dict(primary_counter.most_common(15)).values())
        })

        plt.figure(figsize=(14, 8))
        ax = sns.barplot(x='count', y='primary_category', data=top_primaries)
        plt.title('Distribution of Primary Categories (Top 15)', fontsize=16)
        plt.xlabel('Count', fontsize=14)
        plt.ylabel('Primary Category', fontsize=14)

        # Add count labels
        for i, v in enumerate(top_primaries['count']):
            ax.text(v + 0.5, i, str(v), va='center')

        plt.tight_layout()
        plt.savefig(f"{output_dir}/primary_categories.png", dpi=300)
        plt.close()

        # 7. Category Correlation Network (simplified version)
        # For each paper, we'll count when two categories appear together in tags
        category_pairs = []
        for tags_str in df['all_tags']:
            try:
                tags = ast.literal_eval(tags_str)
                if len(tags) > 1:
                    for i in range(len(tags)):
                        for j in range(i + 1, len(tags)):
                            category_pairs.append((tags[i], tags[j]))
            except:
                continue

        pair_counter = Counter(category_pairs)
        top_pairs = pd.DataFrame({
            'pair': list(dict(pair_counter.most_common(20)).keys()),
            'count': list(dict(pair_counter.most_common(20)).values())
        })

        # Create a bar chart of top pairs
        plt.figure(figsize=(14, 10))
        pair_labels = [f"{pair[0]} & {pair[1]}" for pair in top_pairs['pair']]
        ax = sns.barplot(x=top_pairs['count'], y=pair_labels)
        plt.title('Most Common Tag Pairs in Papers (Top 20)', fontsize=16)
        plt.xlabel('Count', fontsize=14)
        plt.ylabel('Tag Pair', fontsize=14)

        # Add count labels
        for i, v in enumerate(top_pairs['count']):
            ax.text(v + 0.5, i, str(v), va='center')

        plt.tight_layout()
        plt.savefig(f"{output_dir}/tag_pairs.png", dpi=300)
        plt.close()

        # 8. Summary report
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_papers = len(df)
        categories_count = len(df['category'].unique())

        with open(f"{output_dir}/summary_report.txt", "w") as f:
            f.write(f"ArXiv AI Papers Analysis Report\n")
            f.write(f"Generated on: {timestamp}\n\n")
            f.write(f"Total papers analyzed: {total_papers}\n")
            f.write(f"Number of unique categories: {categories_count}\n\n")

            f.write("Top 10 Categories:\n")
            for i, (cat, count) in enumerate(df['category'].value_counts().head(10).items()):
                f.write(f"{i + 1}. {cat}: {count} papers ({count / total_papers * 100:.1f}%)\n")

            f.write("\nTop 10 Tags:\n")
            for i, (tag, count) in enumerate(tag_counter.most_common(10)):
                f.write(f"{i + 1}. {tag}: {count} occurrences\n")

        print(f"Visualizations saved to {output_dir}/")
        return


class ArxivAbstractProcessor:
    """
    A class to process ArXiv papers, extract abstracts and GitHub URLs.
    Includes robust error handling and retry mechanisms.
    """

    def __init__(self, max_retries=3, backoff_factor=0.5, retry_delay=1):
        """
        Initialize the processor with retry parameters.

        Args:
            max_retries (int): Maximum number of retries for HTTP requests
            backoff_factor (float): Backoff factor for retries
            retry_delay (int): Base delay between retries in seconds
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_delay = retry_delay
        self.session = self._create_session()

    def _create_session(self):
        """Create a requests session with retry capabilities and proper headers"""
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Add proper User-Agent header
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 ArxivAbstractProcessor (your-email@example.com)'
        })

        return session

    @staticmethod
    def find_github_url(text):
        """
        Find GitHub URL in the given text.

        Args:
            text (str): Text to search for GitHub URL

        Returns:
            str: GitHub URL if found, else empty string
        """
        if not text or not isinstance(text, str):
            return ""

        github_pattern = r'https?://(?:www\.)?github\.com/[^\s\)\"\']+|github\.com/[^\s\)\"\']+'
        match = re.search(github_pattern, text)
        return match.group(0) if match else ""

    def get_arxiv_abstract(self, url, retry_count=0):
        """
        Fetch abstract and GitHub URL for a given arXiv URL with retry mechanism.
        """
        if not url or not isinstance(url, str) or 'arxiv.org' not in url:
            logger.warning(f"Invalid URL: {url}")
            return {'abstract': '', 'github_url': ''}

        # Convert the abs URL to API URL format
        paper_id = url.split('/abs/')[-1]
        api_url = f"http://export.arxiv.org/api/query?id_list={paper_id}"

        try:
            # Add rate limiting
            logger.debug(f"Fetching API URL: {api_url}")
            time.sleep(3)  # Respect rate limit - 3 seconds between requests

            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()

            # Parse the XML response from API
            soup = BeautifulSoup(response.text, 'xml')

            # Extract abstract from the API response
            abstract_element = soup.find('summary')
            if abstract_element:
                abstract_text = abstract_element.text.strip()

                # Check for GitHub URL in the abstract
                github_url = self.find_github_url(abstract_text)

                return {
                    'abstract': abstract_text,
                    'github_url': github_url
                }
            else:
                logger.warning(f"Abstract not found in API response for {paper_id}")
                return {'abstract': '', 'github_url': ''}

        except Exception as e:
            logger.error(f"Error processing {api_url}: {e}")

            # Retry logic
            if retry_count < self.max_retries:
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.info(f"Retrying {api_url} after {wait_time}s (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self.get_arxiv_abstract(url, retry_count + 1)

            return {'abstract': '', 'github_url': ''}

    def process_dataframe(self, df, limit=None):
        """
        Process DataFrame with ArXiv paper information.

        Args:
            df (pd.DataFrame): DataFrame with paper information
            limit (int, optional): Limit number of papers to process

        Returns:
            pd.DataFrame: Updated DataFrame with abstracts and GitHub URLs
        """
        processed_df = df.copy()

        # Log available columns for debugging
        logger.info(f"Available columns: {list(processed_df.columns)}")

        # Add 'abstract' column if it doesn't exist
        if 'abstract' not in processed_df.columns:
            logger.warning("'abstract' column not found. Adding it to the DataFrame.")
            processed_df['abstract'] = ''

        # Add 'github_url' column if it doesn't exist
        if 'github_url' not in processed_df.columns:
            logger.warning("'github_url' column not found. Adding it to the DataFrame.")
            processed_df['github_url'] = ''

        # Apply limit if specified
        if limit is not None:
            processed_df = processed_df.head(limit)

        logger.info(f"Processing {len(processed_df)} papers")

        # Identify papers with missing abstracts
        missing_abstracts = processed_df['abstract'].isna() | (processed_df['abstract'] == '')
        papers_to_fetch = processed_df[missing_abstracts]

        if len(papers_to_fetch) > 0:
            logger.info(f"Found {len(papers_to_fetch)} papers with missing abstracts")

            # Use tqdm with pandas apply for progress tracking
            tqdm.pandas(desc="Fetching missing abstracts")

            # Only fetch abstracts for papers where they're missing
            results = papers_to_fetch['abs_url'].progress_apply(self.get_arxiv_abstract)
            results_df = pd.DataFrame(results.tolist())

            # Update only the rows with missing abstracts
            for idx, row in results_df.iterrows():
                paper_idx = papers_to_fetch.index[idx]
                if row['abstract']:
                    processed_df.at[paper_idx, 'abstract'] = row['abstract']
                if row['github_url'] and not processed_df.at[paper_idx, 'github_url']:
                    processed_df.at[paper_idx, 'github_url'] = row['github_url']

        return processed_df

    def __call__(self, input_data, limit=None, output_csv=None):
        """
        Process papers from a CSV file or DataFrame.

        Args:
            input_data (str or pd.DataFrame): Path to input CSV file or DataFrame
            limit (int, optional): Limit number of papers to process
            output_csv (str, optional): Path to save output CSV file

        Returns:
            pd.DataFrame: Updated DataFrame with abstracts and GitHub URLs
        """
        # Handle input as either file path or DataFrame
        if isinstance(input_data, str):
            logger.info(f"Reading data from {input_data}")
            df = pd.read_csv(input_data)
        else:
            logger.info("Using provided DataFrame")
            df = input_data.copy()

        logger.info(f"Original DataFrame Shape: {df.shape}")

        # Process the DataFrame
        updated_df = self.process_dataframe(df, limit)

        # Save updated DataFrame if output_csv is specified
        if output_csv:
            logger.info(f"Saving results to {output_csv}")
            updated_df.to_csv(output_csv, index=False)

        logger.info(f"Updated DataFrame Shape: {updated_df.shape}")
        logger.info(f"Abstract column filled: {updated_df['abstract'].notna().sum()}/{len(updated_df)}")

        return updated_df


def get_arxiv_papers(limit = None) -> DataFrame:
    handler = ArxivHandler()
    abs_processor = ArxivAbstractProcessor()
    papers = get_todays_arxiv_papers()
    relevant = handler.get_ai_relevant(papers)
    filtered_df = handler.handle_category(relevant)
    final = abs_processor(filtered_df,limit=limit)
    return final



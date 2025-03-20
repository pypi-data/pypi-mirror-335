"""
    Analyzes a research paper to find relevant sections and answer a query using semantic search
    and clustering.

    Logic flow:
    1. Preprocesses paper text by removing references and extracts initial relevant chunks
       using semantic similarity with the query

    2. For each initial chunk-query pair, generates optimized search queries using an AI model
       to explore different semantic angles of the question

    3. Uses the generated queries to perform another round of semantic search on the paper,
       retrieving additional relevant chunks

    4. Combines and deduplicates all retrieved text chunks to create a comprehensive set of
       potentially relevant segments

    5. Groups similar chunks into k clusters using semantic clustering to identify main themes

    6. Identifies the two largest clusters (most common themes) as they likely represent
       the most relevant topic groups

    7. Combines chunks from the two largest clusters to form the final set of results

    8. Generates a natural language summary of the selected chunks to provide a direct
       answer to the original query
"""
import itertools
from collections import Counter, defaultdict
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

import streamlit as st
import os
from typing import List, Tuple
from dataclasses import dataclass
import sqlite3
from datetime import datetime
import json
from liteutils import read_arxiv, remove_references

from liteauto.searchlite import google
from liteauto.visionlite import wlcluster
import concurrent.futures
import PyPDF2
import io
from litegen import genai
from liteauto.visionlite import wlanswer, wlsimchunks
from liteutils import read_pdf


@dataclass
class ResearchDocument:
    source: str  # URL or filename
    content: str


def init_db():
    conn = sqlite3.connect('research_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            results TEXT NOT NULL,
            model_name TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn


def save_search(conn, query: str, results: List[ResearchDocument], model_name: str):
    c = conn.cursor()
    results_json = json.dumps([{'source': r.source, 'content': r.content} for r in results])
    c.execute('INSERT INTO searches (query, results, model_name) VALUES (?, ?, ?)',
              (query, results_json, model_name))
    conn.commit()


def get_search_history(conn):
    c = conn.cursor()
    c.execute('SELECT id, query, timestamp FROM searches ORDER BY timestamp DESC')
    return c.fetchall()


def get_search_by_id(conn, search_id):
    c = conn.cursor()
    c.execute('SELECT * FROM searches WHERE id = ?', (search_id,))
    return c.fetchone()


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_relevant_chunks(query: str, text: str, k: int = 5) -> List[str]:
    """Get relevant chunks using wlsimchunks"""
    return wlsimchunks(context=text, query=query, k=k)


def prepare_prompt_for_google_queries_generation(pair_of_qc: List[Tuple[str, str]]) -> List[str]:
    _USER_PROMPT = """<context>{context}</context>
        <query>{query}</query>
        [SEARCH_QUERY]:"""
    return [_USER_PROMPT.format(context=context, query=query) for query, context in pair_of_qc]


def get_ai_generated_search_queries(prompts: List[str]) -> List[str]:
    _SYSTEM_PROMPT = """Given a research paper context,You are  search query generator, based on user query and context,
        generate a single ONE search query that one of the best way to search for better  results.

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


def get_chunk_pairs(questions: List[str], text: str) -> List[str]:
    """Get relevant chunks for each generated question"""
    chunks = []
    for question in questions:
        chunk = wlanswer(context=text, query=question, k=2)
        if isinstance(chunk, list):
            chunks.extend(chunk)
        else:
            chunks.append(chunk)
    return chunks


def process_query_with_context(query: str, context: str, k: int = 5) -> List[str]:
    # Get initial relevant chunks
    context = remove_references(context)
    initial_chunks = get_relevant_chunks(query, context, k)

    pair_qc = [(query, c) for c in initial_chunks]

    # Generate questions from chunks
    prompts = prepare_prompt_for_google_queries_generation(pair_qc)

    new_queries = get_ai_generated_search_queries(prompts)

    def wlanswer_func(query):
        return wlsimchunks(context=context, query=query, k=2)

    with ThreadPoolExecutor(max_workers=4) as executor:
        all_chunks = list(executor.map(wlanswer_func, new_queries))

    all_chunks = list(set(itertools.chain.from_iterable(all_chunks)))

    if len(all_chunks)<k:
        k=len(all_chunks)
    cluster_labels, _ = wlcluster(all_chunks, k=k)

    idx = Counter(cluster_labels).most_common()[0]

    try:
        idx2 = Counter(cluster_labels).most_common()[1]
    except:
        idx2 = None


    clustered_chunks = defaultdict(list)
    for i, label in enumerate(cluster_labels):
        clustered_chunks[label].append(all_chunks[i])

    final_chunks = clustered_chunks[idx[0]]  + clustered_chunks[idx2[0]] if idx2 else []

    return final_chunks


def main():
    conn = init_db()
    st.set_page_config(page_title="Research Paper Analyzer", layout="wide")

    st.title("📚 AI-Enhanced Research Paper Analysis")
    # Add custom CSS to reduce spacing
    st.markdown("""
                   <style>
                       .block-container {
                           padding-top: 2rem;
                           padding-bottom: 0rem;
                       }
                       div.stTitle {
                           margin-top: -3rem;
                       }
                   </style>
               """, unsafe_allow_html=True)

    # Settings in sidebar
    with st.sidebar.popover(label="", icon=":material/settings:"):
        model = st.text_input("Select Model", value="qwen2.5:7b-instruct")
        api_key = st.text_input("API Key", value="dsollama", type="password")
        base_url = st.text_input("Base URL", value="http://192.168.170.76:11434/v1")
        k = st.slider("Number of chunks to analyze", 1, 10, 5)

    if st.sidebar.button("Save & Start new chat"):
        os.environ['OPENAI_MODEL_NAME'] = model
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_BASE_URL'] = base_url
        st.success("✅ Settings saved!")

    # Input methods
    input_method = st.sidebar.radio("Choose input method:", ["ArXiv Link", "Upload PDF"])

    if input_method == "ArXiv Link":
        paper_link = st.sidebar.text_input("search or provide paper link")
        if paper_link and 'arxiv' not in paper_link:
            paper_link = google(f"arxiv paper {paper_link}")[0]

        if paper_link:
            with st.spinner("Reading paper..."):
                try:
                    paper_text = read_arxiv(paper_link)
                    st.session_state.paper_text = paper_text
                    st.session_state.paper_source = paper_link
                    st.sidebar.success(f"{paper_link} loaded successfully!")
                except Exception as e:
                    st.error(f"Error reading paper: {str(e)}")
    else:
        uploaded_file = st.sidebar.file_uploader("Upload PDF file", type="pdf")
        if uploaded_file:
            with st.spinner("Processing PDF..."):
                try:
                    paper_text = read_pdf(io.BytesIO(uploaded_file.getvalue()))
                    st.session_state.paper_text = paper_text
                    st.session_state.paper_source = uploaded_file.name
                    st.sidebar.success("PDF processed successfully!")
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

    # Query input
    query = st.chat_input("Enter your research question:")

    if query and hasattr(st.session_state, 'paper_text'):
        with st.spinner("🤖 AI is analyzing the paper..."):
            if not all(k in os.environ for k in ['OPENAI_MODEL_NAME', 'OPENAI_API_KEY', 'OPENAI_BASE_URL']):
                st.error("⚠️ Please save settings first!")
                return

            # Process query and get clustered results
            results = process_query_with_context(query, st.session_state.paper_text, k)

            # Create ResearchDocument objects
            doc_results = [ResearchDocument(source=st.session_state.paper_source, content=r) for r in results]

            # Save to database
            save_search(conn, query, doc_results, os.environ['OPENAI_MODEL_NAME'])

            # Display results
            st.subheader(f"📊 Analysis Results ({len(results)} relevant sections)")
            for idx, result in enumerate(results, 1):
                with st.expander(f"Section {idx}", expanded=False):
                    st.markdown(result)

            # Get AI summary
            summary_prompt = f"Based on these excerpts from the research paper, answer the query: {query}\n\nExcerpts:\n{' '.join(results)}"
            _SYSTEM_PROMPT = """You are Friendly Question answer expert. 
            given excerpts answer the question in user friendly everday basic english for very easy understanding of user."""
            summary = genai(summary_prompt,system_prompt=_SYSTEM_PROMPT)

            st.subheader("AI Answer")
            st.markdown(summary)

    # Display search history
    with st.sidebar:
        st.title("Recents")
        history = get_search_history(conn)
        for search_id, query, timestamp in history:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            if st.button(f"🔍 {query[:30]}... ({dt.strftime('%H:%M')})", key=f"hist_{search_id}"):
                search_data = get_search_by_id(conn, search_id)
                if search_data:
                    _, stored_query, _, results_json, used_model = search_data
                    results = [ResearchDocument(source=r['source'], content=r['content'])
                               for r in json.loads(results_json)]
                    st.info(f"📜 Historical search: '{stored_query}' (using {used_model})")
                    for idx, result in enumerate(results, 1):
                        with st.expander(f"Section {idx}", expanded=False):
                            st.markdown(result.content)


if __name__ == "__main__":
    main()

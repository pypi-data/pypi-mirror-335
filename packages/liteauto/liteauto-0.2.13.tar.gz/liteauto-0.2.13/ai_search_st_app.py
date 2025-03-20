import streamlit as st
import os
from typing import List
from datetime import datetime
import json
from pathlib import Path
from liteauto.ai_web_search.ai_enhanced_search import GoogleSearch, GoogleSearchDocument


def sanitize_filename(query: str) -> str:
    """Sanitize the query to create a valid filename."""
    # Replace invalid filename characters with underscores
    invalid_chars = '<>:"/\\|?*'
    filename = ''.join('_' if c in invalid_chars else c for c in query)
    return filename[:100]  # Limit filename length


def save_search(save_path: Path, query: str, results: List[GoogleSearchDocument], model_name: str):
    """Save search results to a markdown file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sanitized_query = sanitize_filename(query)
    filename = f"{timestamp}_{sanitized_query}.md"
    filepath = save_path / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Search Query: {query}\n\n")
        f.write(f"**Timestamp:** {timestamp}  \n")
        f.write(f"**Model Used:** {model_name}\n\n")
        f.write("## Search Results\n\n")

        for idx, result in enumerate(results, 1):
            f.write(f"### Source {idx}: {result.url}\n\n")
            f.write(f"{result.content}\n\n")
            f.write("---\n\n")


def get_search_history(save_path: Path) -> List[tuple]:
    """Get list of previous searches from markdown files."""
    if not save_path.exists():
        return []

    files = list(save_path.glob("*.md"))
    history = []

    for file in sorted(files, reverse=True):
        # Extract timestamp and query from filename
        filename = file.stem  # Get filename without extension
        timestamp = filename.split('_')[0]
        query = ' '.join(filename.split('_')[1:])

        # Add file path for later retrieval
        history.append((str(file), query, timestamp))

    return history


def get_search_content(file_path: str) -> dict:
    """Read content from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content


def main(save_dir="/home/ntlpt59/Documents/google_ai_docs"):
    # Remove default page margins and padding
    st.set_page_config(page_title="AI-Enhanced Search", layout="wide", initial_sidebar_state="auto")

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

    st.title("🚀 AI-Enhanced MultiSearch")

    # Settings popover
    with st.sidebar.popover(label="", icon=":material/settings:"):
        model = st.text_input(
            "Select Model",
            value="qwen2.5:7b-instruct"
        )

        api_key = st.text_input(
            "API Key",
            value="dsollama",
            type="password"
        )

        base_url = st.text_input(
            "Base URL",
            value="http://192.168.170.76:11434/v1"
        )

        # Add save path input
        save_path = st.text_input(
            "Save Path",
            value=save_dir,
            help="Directory path to save search results"
        )

        k = st.slider("Number of results", 1, 10, 5)

    # Save settings button
    if st.sidebar.button("Save and Start new chat"):
        os.environ['OPENAI_MODEL_NAME'] = model
        os.environ['OPENAI_API_KEY'] = api_key
        os.environ['OPENAI_BASE_URL'] = base_url

        # Create save directory if it doesn't exist
        Path(save_path).mkdir(parents=True, exist_ok=True)
        st.sidebar.success("✅ Settings saved!")

    # Chat history section in sidebar
    st.sidebar.title("Recents")

    save_path_obj = Path(save_path)
    history = get_search_history(save_path_obj)

    for file_path, query, timestamp in history:
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if st.sidebar.button(f"🔍 {query[:30]}... ({dt.strftime('%H:%M')})", key=f"hist_{file_path}"):
            content = get_search_content(file_path)
            st.markdown(content)

    # Search input
    query = st.chat_input("Enter your search query:")

    if query:
        try:
            with st.spinner("🤖 AI is processing your query and searching..."):
                # Verify environment variables are set
                if not all(k in os.environ for k in ['OPENAI_MODEL_NAME', 'OPENAI_API_KEY', 'OPENAI_BASE_URL']):
                    st.error("⚠️ Please save settings first!")
                    return

                # Perform search
                results = GoogleSearch.perform_multi_queries_search(query, doc_k=k)

                # Save to markdown file
                save_search(save_path_obj, query, results, os.environ['OPENAI_MODEL_NAME'])

                # Display results
                st.subheader(f"📊 Search Results ({len(results)} sources)")
                for idx, result in enumerate(results, 1):
                    with st.expander(f"Source {idx}: {result.url}", expanded=True):
                        st.markdown(result.content)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please check your settings and try again.")


if __name__ == "__main__":
    main()
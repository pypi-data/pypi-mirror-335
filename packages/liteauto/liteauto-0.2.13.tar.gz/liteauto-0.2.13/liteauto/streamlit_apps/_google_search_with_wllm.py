import streamlit as st
import pandas as pd
from liteauto.searchlite import google
from liteauto.parselite import parse
from liteauto.visionlite import wlanswer
from liteauto.search_gen._search_gen import SearchGen

gen = SearchGen()

# Initialize session state for chat history and settings
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'max_urls': 5,
        'research_mode': False,
        'code_mode': False,
        'advanced_mode': False
    }


def build_enhanced_queries(base_query):
    if st.session_state.settings['research_mode']:
        base_query = f"{base_query} site:arxiv.org"
    if st.session_state.settings['code_mode']:
        base_query = f"{base_query} site:github.com"
    if st.session_state.settings['advanced_mode']:
        res = gen(base_query,n=5)
        return res
    return [base_query]


def process_query(query, max_urls=5):
    all_results = []
    queries = build_enhanced_queries(query)
    print(f'{queries=}')
    urls = google(query=queries, max_urls=max_urls)

    for idx,q in enumerate(queries):
        # Get URLs from search

        contents = parse(urls=urls[idx], llm=False)
        valid_contents = [c for c in contents if c.content]

        for content in valid_contents:
            top_chunk = wlanswer(content.content, query)
            all_results.append({
                'Query': q,
                'URL': content.url,
                'Relevant Content': top_chunk
            })

    return all_results


def main():
    st.title("AI Search Assistant")

    # Settings bar at the top
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])

    with col1:
        with st.popover("URL Settings"):
            st.session_state.settings['max_urls'] = st.slider(
                "Max URLs per query", 1, 20, 5)

    with col2:
        st.session_state.settings['research_mode'] = st.toggle(
            "Research Papers", st.session_state.settings['research_mode'])

    with col3:
        st.session_state.settings['code_mode'] = st.toggle(
            "Code Search", st.session_state.settings['code_mode'])

    with col4:
        st.session_state.settings['advanced_mode'] = st.toggle(
            "Advanced", st.session_state.settings['advanced_mode'])

    # Chat container for history
    chat_container = st.container()

    # Display chat history
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                with st.chat_message("assistant"):
                    # Group results by query type
                    current_query = None
                    for result in message["content"]:
                        if current_query != result['Query']:
                            current_query = result['Query']
                            if current_query != message["content"][0]['Query']:  # Skip for base query
                                st.markdown(f"**Results for: {current_query}**")

                        with st.expander(f"Source: {result['URL']}", expanded=False):
                            st.markdown("**Relevant Content:**")
                            st.write(result['Relevant Content'])

    # Input area at the bottom
    query = st.chat_input("Ask a question...", key="user_input")

    if query:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": query})

        # Process the query
        with st.spinner("Searching..."):
            results = process_query(
                query, st.session_state.settings['max_urls'])

            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": results})

        # Rerun to update the chat display
        st.rerun()


if __name__ == "__main__":
    main()

    from ollama import chat
    chat()
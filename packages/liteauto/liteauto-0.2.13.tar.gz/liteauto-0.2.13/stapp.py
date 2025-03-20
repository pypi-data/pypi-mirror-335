import streamlit as st
import pandas as pd
import os
from liteauto import (
    google, parse, wlsplit, wlanswer, wltopk, wlsimchunks,
    web, compress, get_summaries, summary, web_top_chunk,
    gmail, automail, project_to_prompt, project_to_markdown,
    get_todays_arxiv_papers, research_paper_analysis,
    deep_research
)

# Set default environment variables if not already set
if 'OPENAI_API_KEY' not in os.environ:
    os.environ['OPENAI_API_KEY'] = 'dsollama'
if 'OPENAI_MODEL_NAME' not in os.environ:
    os.environ['OPENAI_MODEL_NAME'] = 'qwen2.5:7b-instruct'

st.set_page_config(layout="wide", page_title="LiteAuto Tools")


def initialize_session_state():
    if 'api_key' not in st.session_state:
        st.session_state.api_key = 'dsollama'
    if 'base_url' not in st.session_state:
        st.session_state.base_url = None
    if 'model' not in st.session_state:
        st.session_state.model = 'qwen2.5:7b-instruct'

    if 'web_results' not in st.session_state:
        st.session_state.web_result = ""


def main():
    initialize_session_state()

    # st.title("LiteAuto Tools Dashboard")

    # Configuration section in sidebar
    with st.sidebar:
        st.sidebar.title("AI Tools")
        st.header("Configuration")
        st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key)
        st.session_state.base_url = st.text_input("Base URL",
                                                  value=st.session_state.base_url if st.session_state.base_url else "")
        st.session_state.model = st.text_input("Model", value=st.session_state.model)

        # Update environment variables when configuration changes
        if st.button("Update Configuration"):
            os.environ['OPENAI_API_KEY'] = st.session_state.api_key
            if st.session_state.base_url:
                os.environ['OPENAI_BASE_URL'] = st.session_state.base_url
            os.environ['OPENAI_MODEL_NAME'] = st.session_state.model
            st.success("Configuration updated!")

    tabs = st.tabs([
        "ArXiv Research",
        "Project To Prompt",
        "Search & Parse",
        "Text Analysis",
        "Email Tools",
        "Beta"
    ])

    with tabs[0]:
        st.subheader("Analyze Research Paper")
        paper_url = st.text_input("Enter ArXiv paper URL or path")
        if paper_url and st.button("Analyze Paper"):
            with st.spinner("Analyzing paper..."):
                try:
                    analysis = research_paper_analysis(paper_url)

                    # Create tabs for different sections of the analysis
                    analysis_tabs = st.tabs(["Basic Info", "Technical Details", "Summary", "Compression Levels"])

                    # Basic Info Tab
                    with analysis_tabs[0]:
                        st.subheader("Paper Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Title:** {analysis.abs_insights.title}")
                            st.markdown(f"**Year:** {analysis.abs_insights.publication_year}")
                            st.markdown(f"**Authors:** {', '.join(analysis.abs_insights.authors)}")
                            st.markdown(f"**ML Paradigm:** {analysis.abs_insights.ml_paradigm}")
                        with col2:
                            st.markdown(
                                f"**Theoretical Paper:** {'Yes' if analysis.abs_insights.is_theoretical else 'No'}")
                            st.markdown(f"**Contains Code:** {'Yes' if analysis.abs_insights.contains_code else 'No'}")
                            if analysis.abs_insights.code_url and analysis.abs_insights.code_url != "#":
                                st.markdown(f"**Code URL:** {analysis.abs_insights.code_url}")
                            st.markdown(
                                f"**Reproducibility Score:** {analysis.abs_insights.reproducibility_score}/5" if analysis.abs_insights.reproducibility_score else "")

                    # Technical Details Tab
                    with analysis_tabs[1]:
                        st.subheader("Problem & Approach")
                        st.markdown(f"**Problem Statement:**")
                        st.write(analysis.abs_insights.problem_statement)
                        st.markdown(f"**Key Approach:**")
                        st.write(analysis.abs_insights.key_approach)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Technical Components:**")
                            for comp in analysis.abs_insights.technical_components:
                                st.markdown(f"- {comp}")
                        with col2:
                            st.markdown("**Baseline Comparisons:**")
                            for comp in analysis.abs_insights.baseline_comparisons:
                                st.markdown(f"- {comp}")

                        if analysis.abs_insights.datasets_used:
                            st.markdown("**Datasets Used:**")
                            for dataset in analysis.abs_insights.datasets_used:
                                st.markdown(f"- {dataset}")

                    # Summary Tab
                    with analysis_tabs[2]:
                        st.subheader("Summary Insights")

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Problem & Solution**")
                            st.markdown(f"**Problem:** {analysis.summary_insights.problem_statement}")
                            st.markdown(f"**Solution:** {analysis.summary_insights.proposed_solution}")
                            if analysis.summary_insights.key_innovation:
                                st.markdown(f"**Key Innovation:** {analysis.summary_insights.key_innovation}")

                        with col2:
                            st.markdown("**Implementation**")
                            st.markdown(f"**Method Summary:** {analysis.summary_insights.method_summary}")
                            if analysis.summary_insights.key_components:
                                st.markdown("**Key Components:**")
                                for comp in analysis.summary_insights.key_components:
                                    st.markdown(f"- {comp}")

                        st.markdown("**Main Results:**")
                        for result in analysis.summary_insights.main_results:
                            st.markdown(f"- {result}")

                        if analysis.summary_insights.limitations:
                            st.markdown("**Limitations:**")
                            for limitation in analysis.summary_insights.limitations:
                                st.markdown(f"- {limitation}")

                        if analysis.summary_insights.use_cases:
                            st.markdown("**Potential Use Cases:**")
                            for use_case in analysis.summary_insights.use_cases:
                                st.markdown(f"- {use_case}")

                    # Compression Levels Tab
                    with analysis_tabs[3]:
                        st.subheader("Text Compression Levels")

                        compression_level = st.radio(
                            "Select Compression Level",
                            ["Level 5 (Most Compressed)", "Level 4", "Level 3", "Level 2", "Level 1 (Least Compressed)"]
                        )

                        compression_text = {
                            "Level 5 (Most Compressed)": analysis.compress_level5,
                            "Level 4": analysis.compress_level4,
                            "Level 3": analysis.compress_level3,
                            "Level 2": analysis.compress_level2,
                            "Level 1 (Least Compressed)": analysis.compress_level1
                        }

                        st.markdown("**Compressed Text:**")
                        st.write(compression_text[compression_level])

                        if analysis.abstract:
                            with st.expander("Show Original Abstract"):
                                st.write(analysis.abstract)

                except Exception as e:
                    st.error(f"Error analyzing paper: {e}")

        st.header("ArXiv Research Tools")

        if st.button("Get Today's ArXiv Papers"):
            with st.spinner("Fetching papers..."):
                df = get_todays_arxiv_papers()
                st.dataframe(df)
                st.session_state.arxiv_df = df

    # Search & Parse Tab
    with tabs[2]:
        st.header("Search and Parse")

        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("Enter search query")
            max_urls = st.slider("Max URLs to fetch", 1, 20, 5)
            unique_results = st.checkbox("Unique urls only", value=True)

            if st.button("Search"):
                if search_query:
                    with st.spinner("Searching..."):
                        urls = google(search_query, max_urls=max_urls, unique=unique_results)
                        st.session_state.search_results = urls
                        st.write("Search Results:")
                        for url in urls:
                            st.write(url)

        with col2:
            st.subheader("Parse URLs")
            allow_pdf = st.checkbox("Allow PDF extraction", value=True)
            allow_youtube = st.checkbox("Allow YouTube extraction", value=False)
            allow_arxiv = st.checkbox("Use ArXiv Abstract HTML", value=False)

            if st.button("Parse Results"):
                if hasattr(st.session_state, 'search_results'):
                    with st.spinner("Parsing URLs..."):
                        results = parse(
                            st.session_state.search_results,
                            allow_pdf_extraction=allow_pdf,
                            allow_youtube_urls_extraction=allow_youtube,
                            only_abstract=allow_arxiv
                        )
                        st.write("Parsed Content:")
                        for result in results:
                            with st.expander(f"Content from {result.url}"):
                                st.write(result.content)

        # ArXiv Research Tab

    # Text Analysis Tab
    with tabs[3]:
        st.header("Text Analysis Tools")

        text_input = st.text_area("Enter text for analysis")
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Split Text", "Answer Questions", "Find Similar Chunks", "Compress Text"]
        )

        if text_input:
            if analysis_type == "Split Text":
                if st.button("Split Text"):
                    chunks = wlsplit(text_input)
                    for i, chunk in enumerate(chunks, 1):
                        st.write(f"Chunk {i}:")
                        st.write(chunk)
                        st.divider()

            elif analysis_type == "Answer Questions":
                query = st.text_input("Enter your question")
                k = st.slider("Number of relevant chunks", 1, 10, 3)
                if query and st.button("Get Answer"):
                    answer = wlanswer(text_input, query, k=k)
                    st.write("Answer:")
                    st.write(answer)

            elif analysis_type == "Compress Text":
                compress_level = st.slider("Compress levele", 1, 5, 3)
                if st.button("Compress"):
                    with st.spinner(f"Compressing upto level {compress_level}..."):
                        compressed = compress(text_input, n=compress_level)
                        st.write(compressed)

    # Project Analysis Tab
    with tabs[1]:
        st.header("Project Analysis")

        project_path = st.text_input("Enter project directory path")
        analysis_type = st.radio("Analysis Type", ["Generate Prompt", "Generate Markdown"])

        if project_path and st.button("Analyze Project"):
            with st.spinner("Analyzing project..."):
                try:
                    if analysis_type == "Generate Prompt":
                        result = project_to_prompt(project_path)
                    else:
                        result = project_to_markdown(project_path)
                    st.code(result)
                except Exception as e:
                    st.error(f"Error analyzing project: {e}")

    # Email Tools Tab
    with tabs[4]:
        st.header("Email Tools")

        email_type = st.radio("Select Email Function", ["Send Email", "Auto Email Bot"])

        if email_type == "Send Email":
            to_email = st.text_input("To Email")
            subject = st.text_input("Subject")
            body = st.text_area("Email Body")

            if st.button("Send Email"):
                with st.spinner("Sending email..."):
                    success = gmail(body, subject=subject, to_email=to_email)
                    if success:
                        st.success("Email sent successfully!")
                    else:
                        st.error("Failed to send email")

        else:
            st.info("Auto Email Bot Configuration")
            response_time = st.slider("Response check interval (seconds)", 1, 10, 2)
            if st.button("Start Email Bot"):
                st.warning("Email bot will start running. Press Ctrl+C in terminal to stop.")
                try:
                    automail(lambda subject, body: f"Auto-response to: {subject}", sleep_time=response_time)
                except Exception as e:
                    st.error(f"Error: {e}")

    # Beta
    with tabs[5]:
        st.header("Deep Research")

        # Input parameters
        st.subheader("Research Parameters")

        col1, col2 = st.columns(2)

        with col1:
            user_query = st.text_area("Research Query",
                                      placeholder="Enter your research topic or question",
                                      help="What would you like to research?")

            desired_papers = st.number_input(
                "Number of Desired Papers",
                min_value=1,
                max_value=100,
                value=5,
                help="Target number of papers to find"
            )

            min_relevance_score = st.slider(
                "Minimum Relevance Score",
                min_value=0.0,
                max_value=1.0,
                value=0.85,
                step=0.05,
                help="Minimum relevance score for papers (0-1)"
            )

        with col2:
            max_iterations = st.number_input(
                "Maximum Search Iterations",
                min_value=1,
                max_value=20,
                value=3,
                help="Maximum number of search iterations"
            )

            max_urls_per_query = st.number_input(
                "URLs per Query",
                min_value=1,
                max_value=10,
                value=3,
                help="Maximum number of URLs to process per search query"
            )

            months_lookback = st.number_input(
                "Months Lookback",
                min_value=1,
                max_value=60,
                value=12,
                help="How many months to look back in the research"
            )

        # Search button
        if st.button("Start Deep Research"):
            if not user_query:
                st.error("Please enter a research query")
                return

            with st.spinner("Conducting deep research..."):
                try:
                    results = deep_research(
                        user_query=user_query,
                        desired_papers=desired_papers,
                        min_relevance_score=min_relevance_score,
                        max_iterations=max_iterations,
                        max_urls_per_query=max_urls_per_query,
                        months_lookback=months_lookback
                    )

                    # Display results in tabs
                    result_tabs = st.tabs(["Filtered Papers", "Discarded Papers"])

                    # Filtered Papers Tab
                    with result_tabs[0]:
                        st.subheader(f"Filtered Papers ({len(results.filtered_papers)})")
                        for i, paper in enumerate(results.filtered_papers, 1):
                            with st.expander(f"{i}. {paper.title} (Score: {paper.relevance_score:.2f})"):
                                col1, col2 = st.columns([2, 1])

                                with col1:
                                    st.markdown(f"**Summary:**\n{paper.summary}")
                                    if paper.key_findings:
                                        st.markdown(f"**Key Findings:**\n{paper.key_findings}")

                                with col2:
                                    st.markdown(f"**URL:** [{paper.url}]({paper.url})")
                                    if paper.citation_count is not None:
                                        st.markdown(f"**Citations:** {paper.citation_count}")
                                    if paper.publication_date:
                                        st.markdown(f"**Published:** {paper.publication_date}")
                                    if paper.paper_hash:
                                        st.markdown(f"**Paper Hash:** `{paper.paper_hash}`")

                    # Discarded Papers Tab
                    with result_tabs[1]:
                        st.subheader(f"Discarded Papers ({len(results.discarded_papers)})")
                        for i, paper in enumerate(results.discarded_papers, 1):
                            with st.expander(f"{i}. {paper.title} (Score: {paper.relevance_score:.2f})"):
                                st.markdown(f"**Summary:**\n{paper.summary}")
                                st.markdown(f"**URL:** [{paper.url}]({paper.url})")
                                if paper.publication_date:
                                    st.markdown(f"**Published:** {paper.publication_date}")

                except Exception as e:
                    st.error(f"Error during research: {str(e)}")


if __name__ == "__main__":
    main()

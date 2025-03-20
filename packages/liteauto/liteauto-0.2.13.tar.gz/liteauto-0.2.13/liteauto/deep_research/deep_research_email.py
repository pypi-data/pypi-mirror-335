import os
import argparse
import logging
import tempfile
from datetime import datetime
from liteauto import GmailAutomation
from .main import DeepResearchSystem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main(max_urls=1, deep_focus_k=1, sleep_time=10, max_iterations=None,
                        openai_api_key=None, openai_base_url=None, openai_model=None):
    """
    Run an email service that performs deep research on incoming queries and responds with PDF reports.
    Uses md2pdf for Markdown to PDF conversion.

    Args:
        max_urls: Maximum number of URLs to process per search query
        deep_focus_k: Number of frequent URLs to analyze in depth
        sleep_time: Time between checking emails (in seconds)
        max_iterations: Dictionary defining max iterations for each research phase
        openai_api_key: OpenAI API key (defaults to environment variable)
        openai_base_url: OpenAI API base URL (defaults to environment variable or official endpoint)
        openai_model: OpenAI model name to use (defaults to environment variable or gpt-4)
    """
    # Initialize research system with reasonable defaults
    if max_iterations is None:
        max_iterations = {
            "discovery": 1,
            "focused": 1,
            "validation": 1,
            "comparison": 1
        }

    # Configure OpenAI settings
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    if openai_base_url:
        os.environ["OPENAI_API_BASE"] = openai_base_url
    if openai_model:
        os.environ["OPENAI_MODEL"] = openai_model

    research_system = DeepResearchSystem(max_iterations_per_phase=max_iterations)

    def handle_email(subject, body, sender_email):
        """Process incoming email and return research results"""
        logger.info(f"Received research query: {body}")

        # Use subject if body is empty or too short
        query = body.strip() if len(body.strip()) > 10 else subject.strip()

        # Run the deep research on the query
        try:
            logger.info(f"Starting research on: {query}")
            # The updated conduct_research now returns a tuple (final_report, markdown_content)
            final_report, markdown_content = research_system.conduct_research(query, max_urls, deep_focus_k,
                                                                              save_md_report=None)

            temp_dir = tempfile.mkdtemp(prefix="research_")

            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            from md2pdf.core import md2pdf

            pdf_filename = f"research_report_{timestamp}.pdf"
            pdf_path = os.path.join(temp_dir, pdf_filename)

            # Create a simple CSS for better styling
            css_content = """
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.5;
            }
            h1 {
                color: #2c3e50;
            }
            h2 {
                color: #3498db;
                margin-top: 30px;
            }
            h3 {
                color: #2980b9;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
                text-align: left;
            }
            code {
                background-color: #f8f8f8;
                padding: 2px 4px;
                border-radius: 4px;
            }
            pre {
                background-color: #f8f8f8;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }
            """

            # Save CSS to a temporary file
            css_path = os.path.join(temp_dir, f"style_{timestamp}.css")
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)  # Your existing CSS content

            # Generate PDF from the markdown file
            md2pdf(
                pdf_file_path=pdf_path,
                md_content=markdown_content,
                css_file_path=css_path
            )

            logger.info(f"Generated PDF report: {pdf_path}")


            # Prepare response - send PDF if available, otherwise send markdown
            response_message = f"Deep research completed on: {query}\n\n"
            response_message += "Please find the attached research report PDF."
            return (response_message, [pdf_path])

        except Exception as e:
            logger.error(f"Error performing research: {str(e)}")
            return f"Error performing research: {str(e)}"

    # Initialize and start Gmail automation with our handler
    gmail = GmailAutomation(response_func=handle_email)
    logger.info("Deep Research Email service started! Waiting for emails...")
    gmail.start(sleep_time=sleep_time)


def deep_research_email():
    """
    Command-line interface for the deep_research_email function.
    Allows customizing research parameters via command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Run deep research email service')

    # Add arguments with reasonable defaults
    parser.add_argument('--max-urls', type=int, default=5,
                        help='Maximum number of URLs to process per search query (default: 3)')

    parser.add_argument('--deep-focus', type=int, default=2,
                        help='Number of frequent URLs to analyze in depth (default: 1)')

    parser.add_argument('--sleep-time', type=int, default=60,
                        help='Time between checking emails in seconds (default: 60)')

    # Add iteration parameters for each research phase
    parser.add_argument('--discovery-iter', type=int, default=2,
                        help='Max iterations for discovery phase (default: 1)')

    parser.add_argument('--focused-iter', type=int, default=2,
                        help='Max iterations for focused phase (default: 1)')

    parser.add_argument('--validation-iter', type=int, default=2,
                        help='Max iterations for validation phase (default: 1)')

    parser.add_argument('--comparison-iter', type=int, default=2,
                        help='Max iterations for comparison phase (default: 1)')

    # Add OpenAI API configuration options
    parser.add_argument('--openai-api-key', type=str,default="dsollama",
                        help='OpenAI API key (defaults to  dsollama , set : OPENAI_API_KEY environment variable)')

    parser.add_argument('--openai-base-url', type=str,default="http://192.168.170.76:11434/v1",
                        help='OpenAI API base URL (defaults to / http://192.168.170.76:11434/v1/ or set: OPENAI_API_BASE environment variable )')

    parser.add_argument('--openai-model', type=str, default="qwen2.5:7b-instruct",
                        help='OpenAI model name to use (default: qwen2.5:7b-instruct) or set OPENAI_MODEL_NAME')

    args = parser.parse_args()

    # Create max_iterations dictionary from args
    max_iterations = {
        "discovery": args.discovery_iter,
        "focused": args.focused_iter,
        "validation": args.validation_iter,
        "comparison": args.comparison_iter
    }

    # Call the deep_research_email function with parsed arguments
    main(
        max_urls=args.max_urls,
        deep_focus_k=args.deep_focus,
        sleep_time=args.sleep_time,
        max_iterations=max_iterations,  # Pass the max_iterations dictionary
        openai_api_key=args.openai_api_key,
        openai_base_url=args.openai_base_url,
        openai_model=args.openai_model
    )


if __name__ == "__main__":
    deep_research_email()
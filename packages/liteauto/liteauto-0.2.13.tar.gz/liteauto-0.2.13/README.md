# LiteAuto 🚀

[![PyPI version](https://badge.fury.io/py/liteauto.svg)](https://badge.fury.io/py/liteauto)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LiteAuto is a lightweight Python library that provides easy-to-use tools for web automation, content parsing, vision AI, and smart searching. It's designed to be simple yet powerful, making common automation tasks effortless.

## 📦 Installation

```bash
pip install liteauto
```

## ✨ Features

- 🔍 Smart Google search with multi-query support
- 📄 Fast content parsing from web pages and PDFs
- 🧠 Vision AI for content analysis
- 📧 Gmail automation
- 📚 arXiv paper analysis
- 🔄 Project to prompt conversion
- 🎯 Word-level text operations

## 🚀 Quick Start

### Web Search and Parsing

```python
from liteauto import google, parse

# Simple Google search
urls = google("python programming", max_urls=5)

# Parse web content
contents = parse(urls)
for content in contents:
    print(f"URL: {content.url}")
    print(f"Content: {content.content[:200]}...")
```

### Vision AI Features

```python
from liteauto import visionai, wlanswer, wlsplit

# Get AI-powered search results
results = visionai("machine learning fundamentals", k=3)
print(results)

# Split text into meaningful chunks
chunks = wlsplit(long_text)

# Get relevant answers from context
answer = wlanswer(context="long text...", query="specific question", k=1)
```

### Gmail Automation

```python
from liteauto import gmail, automail

# Send a simple email
gmail(body="Hello World!", 
      subject="Test Email", 
      to_email="recipient@example.com")

# Create an automated email responder
def auto_response(subject, body):
    return f"Auto-reply to: {subject}"

automail(auto_response, sleep_time=2)
```

### arXiv Integration

```python
from liteauto import get_todays_arxiv_papers, research_paper_analysis

# Get today's arXiv papers
papers_df = get_todays_arxiv_papers()

# Analyze a research paper
paper_insights = research_paper_analysis("https://arxiv.org/pdf/2301.00001.pdf")
print(paper_insights.summary_insights)
```

### Project Analysis

```python
from liteauto import ProjectToPrompt, project_to_markdown

# Convert project to documentation
project = ProjectToPrompt("path/to/project")
docs = project.generate_markdown()

# Generate markdown from project
markdown = project_to_markdown("path/to/project")
```

## 📚 Main Components

```python
from liteauto import (
    # Search and parsing
    google,          # Google search functionality
    parse,          # Web content parser
    aparse,         # Async web content parser
    
    # Vision AI
    visionai,       # Advanced vision AI search
    minivisionai,   # Lightweight vision AI
    deepvisionai,   # Deep vision AI analysis
    
    # Text operations
    wlanswer,       # Get answers from context
    wlsplit,        # Split text into chunks
    wlsimchunks,    # Get similar chunks
    wltopk,         # Get top-k similar items
    
    # Email
    gmail,          # Gmail operations
    automail,       # Email automation
    GmailAutomation,# Full Gmail automation class
    
    # arXiv
    get_todays_arxiv_papers,    # Get recent arXiv papers
    research_paper_analysis,    # Analyze research papers
    
    # Project tools
    ProjectToPrompt,           # Convert project to prompts
    project_to_markdown        # Convert project to markdown
)
```

## 🛠️ Advanced Usage

### Custom Search Configuration

```python
# Configure advanced search parameters
urls = google(
    query="python tutorials",
    max_urls=10,
    animation=False,
    allow_pdf_extraction=True,
    allow_youtube_urls_extraction=True
)
```

### Vision AI with Custom Parameters

```python
results = visionai(
    query="deep learning applications",
    max_urls=15,
    k=10,
    model="llama3.2:1b-instruct-q4_K_M",
    temperature=0.05,
    genai_query_k=7,
    query_k=15
)
```

### Automated Paper Analysis

```python
from liteauto import research_paper_analysis

paper = research_paper_analysis("paper_url.pdf")
print(f"Problem Statement: {paper.abs_insights.problem_statement}")
print(f"Key Approach: {paper.abs_insights.key_approach}")
print(f"Main Findings: {paper.summary_insights.main_results}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ✨ Contributors

<a href="https://github.com/yourusername/liteauto/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/liteauto" />
</a>

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/liteauto&type=Date)](https://star-history.com/#yourusername/liteauto&Date)
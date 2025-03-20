from litegen import LLM
from liteutils import read_arxiv, extract_abstract, remove_references, read_pdf
from pydantic import BaseModel, Field
from typing import List, Optional

from .. import compress_sequential
from liteauto.utils.common import compress


class PaperInsights(BaseModel):
    # Basic ResearchPaperAnalysis Information
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of paper authors")
    publication_year: int = Field(..., description="Year of publication")

    # Problem and Solution
    problem_statement: str = Field(..., description="The main problem or challenge the paper addresses")
    is_novel_problem: bool = Field(default=False, description="Whether the problem itself is newly identified")

    # Methodology
    key_approach: str = Field(..., description="Main method or approach proposed")
    technical_components: List[str] = Field(default_factory=list,
                                            description="Key technical components or algorithms used")
    baseline_comparisons: List[str] = Field(default_factory=list, description="Methods compared against")

    # Implementation Details
    contains_code: bool = Field(default=False, description="Whether the paper includes code")
    code_url: Optional[str] = Field(None, description="URL to the code repository if available")
    datasets_used: List[str] = Field(default_factory=list, description="Datasets used in the paper")

    # Results and Contributions
    key_findings: str = Field(description="Main results and findings")

    ml_paradigm: str = Field(..., description="Type of ML (supervised/unsupervised/reinforcement/etc.)")
    requires_special_hardware: bool = Field(default=False,
                                            description="Whether special hardware (like GPUs) is required")

    # Meta Information
    is_theoretical: bool = Field(default=False, description="Whether the paper is primarily theoretical")
    reproducibility_score: Optional[float] = Field(None, description="Score for reproducibility of results (0-1)")


class SummaryInsights(BaseModel):
    # Core Problem & Solution
    problem_statement: str = Field(..., description="Main problem the paper addresses")
    proposed_solution: str = Field(..., description="Key solution/approach proposed")
    key_innovation: Optional[str] = Field(None, description="What's new/different about this approach")

    # Technical Details
    method_summary: str = Field(..., description="Brief overview of methodology")
    key_components: List[str] = Field(default_factory=list, description="Main technical components used")

    # Results & Impact
    main_results: List[str] = Field(default_factory=list, description="Key findings and results")
    limitations: List[str] = Field(default_factory=list, description="Known limitations or constraints")

    # Implementation
    has_code: bool = Field(default=False, description="Whether code is available")
    code_url: Optional[str] = Field(None, description="Link to code if available")

    # Applications
    use_cases: List[str] = Field(default_factory=list, description="Potential applications of the work")


class ResearchPaperAnalysis(BaseModel):
    abs_insights: PaperInsights
    summary_insights: SummaryInsights
    compress_level5: str
    compress_level4: str
    compress_level3: str
    compress_level2: str
    compress_level1: str
    text: str
    raw_ocr_text: str
    abstract: Optional[str] = None

    def __str__(self):
        return (f"**abs_insights**: {self.abs_insights}\n"
                f"**summary_insights**: {self.summary_insights}\n"
                f"**compress_level3**: {self.compress_level3}\n"
                f"**abstract**: {self.abstract}")


def research_paper_analysis(pdf_path_or_url,compress_paralle=True):
    llm = LLM()
    text = read_arxiv(pdf_path_or_url) if 'https' in pdf_path_or_url else read_pdf(pdf_path_or_url)
    abs = extract_abstract(text)
    main_text = remove_references(text)

    compress_func = compress if compress_paralle else compress_sequential
    l1 = compress_func(main_text)
    l2 = compress_func(l1)
    l3 = compress_func(l2)
    l4 = compress_func(l3)
    l5 = compress_func(l4)
    abs_insights = llm(prompt=f'given research paper abstract generate insights, Abstract : {abs}',
                       response_format=PaperInsights)
    summary_insights = llm(prompt=f'given research paper summary generate insights, Summary : {l4}',
                           response_format=SummaryInsights)

    paper = ResearchPaperAnalysis(
        abs_insights=abs_insights,
        summary_insights=summary_insights,
        compress_level5=l5,
        compress_level4=l4,
        compress_level3=l3,
        compress_level2=l2,
        compress_level1=l1,
        text=main_text,
        abstract=abs,
        raw_ocr_text=text
    )
    return paper
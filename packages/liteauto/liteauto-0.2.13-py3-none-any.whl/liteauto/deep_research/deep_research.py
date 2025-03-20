from datetime import datetime
from typing import List, Dict, Optional, Literal, Union, Any
from pydantic import BaseModel, Field
import nltk
from collections import defaultdict, Counter
import json
import re
import time
import logging
from litegen import LLM
# from ..searchlite import google
# from ..parselite import parse
from liteauto import google,parse

from pydantic import create_model

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Models from the provided document
class Constraint(BaseModel):
    """
    Represents a constraint on the research query.
    """
    type: str = Field(...,
                      description="Type of constraint (e.g., 'budget', 'time', 'quality', 'quantity', 'domain', 'methodology', 'ethical')")
    value: Union[str, int, float, bool] = Field(...,
                                                description="The constraint value (could be numeric, textual, or boolean)")
    operator: Optional[
        Literal["equals", "less_than", "greater_than", "between", "includes", "excludes", "min", "max"]] = Field(
        None, description="Optional operator specifying how the constraint should be applied"
    )
    unit: Optional[str] = Field(None,
                                description="Optional unit for numeric constraints (e.g., 'USD', 'pages', 'years')")
    importance: Literal["critical", "high", "medium", "low", "optional"] = Field(
        "medium", description="Importance level of this constraint for the research"
    )
    description: Optional[str] = Field(None, description="Optional detailed description of the constraint")


class UserIntent(BaseModel):
    domain: str = Field(..., description="Primary research domain of the query")
    intent_type: Literal["comparison", "recommendation", "information", "analysis", "trend"] = Field(...,
                                                                                                     description="Primary intent classification")
    temporal_scope: Literal["recent", "historical", "current", "future", "timeless"] = Field(...,
                                                                                             description="Temporal scope of information needed")
    key_entities: List[str] = Field(..., description="Main entities or concepts to be researched")
    constraints: List[Constraint] = Field(default_factory=list,
                                          description="Key constraints ")
    primary_success_criteria: List[str] = Field(default_factory=list,
                                                description="Key indicators that the research was successful")
    expected_output: str = Field(..., description="What type of result the user is looking for")
    geo_context: Optional[str] = Field(None, description="Geographical context if detectable")


# Search related models
class SearchQuery(BaseModel):
    query: str = Field(..., description="Generated search query based on research intent and focus")
    focus: str = Field(..., description="What aspect of the research this query is focusing on")
    priority: int = Field(..., description="Priority level of this query (1-5, with 1 being highest)")


class ResearchResult(BaseModel):
    url: str
    title: str = ""
    content: str = ""
    relevance_score: float = 0.0
    credibility_score: float = 0.0
    phase: str = ""
    key_insights: List[str] = Field(default_factory=list)
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    search_query: str = ""


class ResearchSummary(BaseModel):
    key_findings: List[str] = Field(default_factory=list)
    entity_insights: Dict[str, List[str]] = Field(default_factory=dict)
    validated_facts: List[str] = Field(default_factory=list)
    comparisons: List[Dict[str, Any]] = Field(default_factory=list)
    constraints_met: List[str] = Field(default_factory=list)
    constraints_unmet: List[str] = Field(default_factory=list)
    knowledge_gaps: List[str] = Field(default_factory=list)
    confidence_level: float = 0.0


class DeepResearchSystem:
    def __init__(self, max_iterations_per_phase=None):
        self.llm = LLM("dsollama")
        self.current_phase = "discovery"
        # Add system prompt footer
        self.system_prompt_footer = self._get_system_prompt_footer()

        self.max_iterations_per_phase = max_iterations_per_phase or {
            "discovery": 3,
            "focused": 2,
            "validation": 2,
            "comparison": 3
        }
        self.phase_iterations = {
            "discovery": 0,
            "focused": 0,
            "validation": 0,
            "comparison": 0
        }
        self.intent = None
        self.search_results = []
        self.research_results = []
        self.phase_summaries = {
            "discovery": {},
            "focused": {},
            "validation": {},
            "comparison": {}
        }
        self.final_summary = None
        self.previous_queries = set()
        self.processed_urls = set()  # Track URLs we've already processed
        self.learning_context = {
            "successful_terms": Counter(),
            "unsuccessful_terms": Counter(),
            "entity_mentions": Counter(),
            "relevance_by_source": defaultdict(list)
        }
        self.geo_context = None
        self.currency_context = "RUPEES"  # Default currency
        self.max_query_similarity = 0.7  # Similarity threshold for deduplication

    def _get_system_prompt_footer(self) -> str:
        """Get the system prompt footer with current date and time"""
        from datetime import datetime
        current_time = datetime.now()
        footer = f"""

        ===================================
        Generated on: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
        Year: {current_time.year}
        ===================================
        """
        return footer

    def _append_footer_to_prompt(self, system_prompt: str) -> str:
        """Append the footer to a system prompt"""
        if not system_prompt:
            return self.system_prompt_footer
        return f"{system_prompt}\n{self.system_prompt_footer}"

    def _llm_call(self, system_prompt: str = None, prompt: str = None, response_format: Any = None) -> Any:
        """Helper method to make LLM calls with the footer appended to system prompts"""
        system_prompt_with_footer = self._append_footer_to_prompt(system_prompt)
        return self.llm(
            system_prompt=system_prompt_with_footer,
            prompt=prompt,
            response_format=response_format
        )

    def analyze_intent(self, query: str) -> UserIntent:
        """Analyze the user's research intent with geo context awareness"""
        # First detect geographical context

        system_prompt = """
        You are a specialized query analyzer for an advanced DeepResearch system designed to understand complex research needs. Your task is to extract structured intent from user queries that will guide comprehensive automated research.

        INSTRUCTIONS:
        Extract the following from each query:

        1. DOMAIN: Identify the primary research domain (e.g., AI research, product recommendation, market analysis)

        2. INTENT TYPE: Classify the primary intent as one of:
           - Comparison: Evaluating multiple items against each other
           - Recommendation: Seeking suggestions based on criteria
           - Information: Requesting factual data or explanations
           - Analysis: Seeking deeper understanding of patterns or relationships
           - Trend: Looking for emerging or evolving patterns over time

        3. TEMPORAL SCOPE: Determine when the information should be from:
           - Recent: Latest information (e.g., "latest papers", "current trends")
           - Historical: Past information (e.g., "evolution of", "over the past decade")
           - Current: Present state (e.g., "available now", "existing solutions")
           - Future: Predictions or upcoming developments
           - Timeless: Not time-sensitive information

        4. KEY ENTITIES: Extract 2-5 main entities or concepts that need to be researched

        5. CONSTRAINTS: Identify specific limitations or requirements (e.g., budget limits, quantity specifications, quality thresholds)

        6. PRIMARY SUCCESS CRITERIA: List 2-4 key indicators that would signal to the user that their research needs have been met (e.g., finding specific metrics, identifying particular alternatives, uncovering certain relationships)

        7. EXPECTED OUTPUT: Determine what form of output the user wants (e.g., list of options, detailed comparison, explanation, synthesis of findings)

        8. GEO CONTEXT: If detectable, identify the geographical or regional context of the query

        Analyze the query structurally and semantically. Look for both explicit statements and implicit needs based on query construction and domain knowledge.
        """

        logger.info(f"Analyzing intent for query: {query}")
        intent = self._llm_call(
            system_prompt=system_prompt,
            prompt=query,
            response_format=UserIntent
        )
        logger.info(f"Intent analysis result: {intent}")

        # Apply currency context to constraints if relevant
        for constraint in intent.constraints:
            if constraint.type == "budget" and isinstance(constraint.value, (int, float)) and not constraint.unit:
                constraint.unit = self.currency_context
                logger.info(f"Applying currency context to constraint: {constraint}")

        self.intent = intent
        logger.info(f"Final intent set: {self.intent}")
        return intent

    def analyze_pos_tags(self, query: str):
        """Analyze POS tags in the query to better understand it"""
        # Download necessary NLTK resources
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)

        # Tokenize and tag
        tokens = nltk.word_tokenize(query)
        pos_tags = nltk.pos_tag(tokens)
        logger.info(f"POS tags for query '{query}': {pos_tags}")

        # Organize by POS
        tagged_words = defaultdict(list)
        for word, tag in pos_tags:
            tagged_words[tag].append(word)
        logger.info(f"Organized POS tags: {tagged_words}")

        return tagged_words

    def get_phase_focus(self):
        """Get the current research focus based on the phase"""
        focus = {}

        if self.current_phase == "discovery":
            focus["goal"] = "broad_understanding"
            focus["search_strategy"] = "general_search"
            focus["search_priority"] = "breadth"

        elif self.current_phase == "focused":
            focus["goal"] = "constraint_satisfaction"
            focus["search_strategy"] = "targeted_search"
            focus["search_priority"] = "precision"

        elif self.current_phase == "validation":
            focus["goal"] = "fact_verification"
            focus["search_strategy"] = "verification_search"
            focus["search_priority"] = "reliability"

        elif self.current_phase == "comparison":
            focus["goal"] = "direct_comparison"
            focus["search_strategy"] = "comparison_search"
            focus["search_priority"] = "depth"

        logger.info(f"Current phase focus: {focus}")
        return focus

    def is_similar_query(self, query: str) -> bool:
        """Check if a query is too similar to previously executed queries using WordLlama"""
        # Exact match check
        if query in self.previous_queries:
            logger.info(f"Query '{query}' already exists in previous queries.")
            return True

        # Initialize WordLlama if not already done
        if not hasattr(self, 'wordllama'):
            try:
                from wordllama import WordLlama
                logger.info("Initializing WordLlama for query similarity detection")
                self.wordllama = WordLlama.load()  # Load the default model
            except ImportError:
                logger.warning("WordLlama not available. Falling back to Jaccard similarity.")
                self.wordllama = None

        # Use WordLlama for similarity if available
        if hasattr(self, 'wordllama') and self.wordllama:
            for prev_query in self.previous_queries:
                similarity = self.wordllama.similarity(query, prev_query)

                if similarity > self.max_query_similarity:
                    logger.info(
                        f"Query '{query}' is semantically similar (score={similarity:.2f}) to previous query '{prev_query}'.")
                    return True
        else:
            # Fallback to Jaccard similarity if WordLlama is not available
            query_words = set(query.lower().split())

            for prev_query in self.previous_queries:
                prev_words = set(prev_query.lower().split())

                # Calculate Jaccard similarity
                intersection = len(query_words.intersection(prev_words))
                union = len(query_words.union(prev_words))

                similarity = intersection / union if union > 0 else 0

                if similarity > self.max_query_similarity:
                    logger.info(
                        f"Query '{query}' is too similar (similarity={similarity:.2f}) to previous query '{prev_query}'.")
                    return True

        logger.info(f"Query '{query}' is not similar to previous queries.")
        return False

    def generate_search_queries(self, num_queries: int = 3) -> List[SearchQuery]:
        """Generate search queries based on intent and current phase with context awareness"""

        class QueryList(BaseModel):
            queries: List[SearchQuery]

        focus = self.get_phase_focus()

        # Add learning context to guide query generation
        learning_insights = {
            "successful_terms": dict(self.learning_context["successful_terms"].most_common(5)),
            "unsuccessful_terms": dict(self.learning_context["unsuccessful_terms"].most_common(5)),
            "top_entities": dict(self.learning_context["entity_mentions"].most_common(5))
        }
        logger.info(f"Learning insights for query generation: {learning_insights}")

        # Identify constraints for query generation
        constraints_text = ""
        if self.intent.constraints:
            constraints_list = []
            for constraint in self.intent.constraints:
                unit_text = f" {constraint.unit}" if constraint.unit else ""
                constraints_list.append(f"{constraint.type}: {constraint.value}{unit_text}")
            constraints_text = "\nConstraints: " + ", ".join(constraints_list)
        logger.info(f"Constraints for query generation: {constraints_text}")

        # Add previously executed queries to avoid repetition
        previous_queries_text = ""
        if self.previous_queries:
            previous_queries_text = "\nPreviously executed queries (avoid repeating these):\n- " + "\n- ".join(
                list(self.previous_queries)[-5:])
        logger.info(f"Previous queries (to avoid): {previous_queries_text}")

        system_prompt = f"""
        You are a research query generator for a DeepResearch system. Generate {num_queries} search queries 
        that will help with research in the current phase.

        Current research phase: {self.current_phase}
        Phase goal: {focus["goal"]}
        Search strategy: {focus["search_strategy"]}
        Search priority: {focus["search_priority"]}

        Research intent:
        - Domain: {self.intent.domain}
        - Intent type: {self.intent.intent_type}
        - Temporal scope: {self.intent.temporal_scope}
        - Key entities: {", ".join(self.intent.key_entities)}{constraints_text}

        IMPORTANT: Focus exclusively on the key entities and research intent above. 
        Do not include geographical limitations unless they were specifically mentioned in the original query.
        For technical topics like AI, ML, or programming, maintain a global perspective unless location is critical.

        Learning from previous searches:
        - Effective search terms: {learning_insights['successful_terms']}
        - Less effective terms: {learning_insights['unsuccessful_terms']}
        - Most relevant entities: {learning_insights['top_entities']}
        {previous_queries_text}

        Generate queries that are:
        1. Specific and focused on finding information that matches the current phase
        2. Diverse to cover different aspects of the research need
        3. Formulated to work well with search engines
        4. Prioritized by importance (1 = highest priority, 5 = lowest)
        5. NOT similar to previously executed queries

        Return a list of {num_queries} search queries.
        """

        logger.info(f"Generating {num_queries} search queries for phase: {self.current_phase}")
        queries = self._llm_call(
            system_prompt=system_prompt,
            prompt=f"""Generate search queries for the current research phase.
            Research intent:
        - Domain: {self.intent.domain}
        - Intent type: {self.intent.intent_type}
        - Temporal scope: {self.intent.temporal_scope}
        - Key entities: {", ".join(self.intent.key_entities)}{constraints_text}
            """,
            response_format=QueryList
        )
        logger.info(f"Generated raw queries: {queries}")

        # Filter out similar queries
        filtered_queries = []
        for query in queries.queries:
            if not self.is_similar_query(query.query):
                filtered_queries.append(query)
                self.previous_queries.add(query.query)
            else:
                logger.info(f"Skipping similar query: {query.query}")

        # If we filtered out too many, generate some replacements
        if len(filtered_queries) < num_queries // 2 and len(filtered_queries) > 0:
            logger.info("Too many similar queries filtered out, generating replacements")

            # Add what we have so far to previous queries
            for query in filtered_queries:
                self.previous_queries.add(query.query)

            # Request some more with stronger constraints against similarity
            system_prompt += "\n\nIMPORTANT: Your previous suggestions were too similar to past queries. Generate more user intent different queries"

            additional_queries = self._llm_call(
                system_prompt=system_prompt,
                prompt="Generate new, dissimilar search queries that haven't been tried before.",
                response_format=QueryList
            )
            logger.info(f"Generated additional queries: {additional_queries}")

            for query in additional_queries.queries:
                if not self.is_similar_query(query.query):
                    filtered_queries.append(query)
                    self.previous_queries.add(query.query)

                if len(filtered_queries) >= num_queries:
                    break

        # # Ensure at least one query
        # if not filtered_queries and self.intent is not None:
        #     logger.warning("No queries generated, creating a fallback query.")
        #     # Create a fallback query
        #     fallback_query = SearchQuery(
        #         query=f"{' '.join(self.intent.key_entities)} {self.intent.domain}",
        #         focus="general information",
        #         priority=1
        #     )
        #     filtered_queries.append(fallback_query)
        #     self.previous_queries.add(fallback_query.query)

        logger.info(f"Final filtered queries: {filtered_queries}")
        return filtered_queries

    def _update_learning_context_unsuccessful(self, query: str):
        """Update learning context for unsuccessful terms"""
        query_terms = query.lower().split()
        for term in query_terms:
            if len(term) > 3:  # Only track meaningful terms
                self.learning_context["unsuccessful_terms"][term] += 1
        logger.info(f"Updated learning context with unsuccessful terms: {query_terms}")

    def execute_search(self, query: str, max_urls) -> List[Dict]:
        """Execute a search query and collect results with error handling"""
        logger.info(f"Executing search for query: {query}")
        try:
            # Get URLs from search
            urls = google(query, max_urls=max_urls * 2)  # Request more to account for filtering
            urls = [url.replace("html", "pdf") if 'arxiv.org' in url else url for url in urls]  # html -> pdf for arxiv.

            if not urls:
                logger.warning(f"No URLs found for query: {query}")
                return []

                # Track URL frequency - even for URLs we've seen before
            for url in urls:
                self.url_frequency[url] += 1

            # Filter out previously processed URLs
            unique_urls = [url for url in urls if url not in self.processed_urls]

            if not unique_urls:
                logger.warning(f"No new URLs found for query: {query}, all have been processed before")
                # Update learning context for unsuccessful terms
                self._update_learning_context_unsuccessful(query)
                return []

            logger.info(f"Found {len(unique_urls)} new URLs out of {len(urls)} total")

            # Process only up to max_urls new URLs
            urls_to_process = unique_urls[:max_urls]

            # Add these URLs to our processed set before parsing
            for url in urls_to_process:
                self.processed_urls.add(url)

            # Process all URLs in a single batch
            try:
                responses = parse(urls_to_process)
                if not responses:
                    logger.warning(f"No content parsed from URLs for query: {query}")
                    return []

                # Filter and format valid responses
                valid_responses = []
                for resp in responses:
                    if resp and resp.content:
                        valid_responses.append({
                            "url": resp.url,
                            "content": resp.content
                        })

                if not valid_responses:
                    logger.warning(f"No valid content found in parsed responses for query: {query}")
                    # Update learning context for unsuccessful terms
                    query_terms = query.lower().split()
                    for term in query_terms:
                        if len(term) > 3:  # Only track meaningful terms
                            self.learning_context["unsuccessful_terms"][term] += 1
                    logger.info(f"Updated learning context with unsuccessful terms: {query_terms}")

                return valid_responses

            except Exception as e:
                logger.error(f"Error parsing URLs for query '{query}': {str(e)}")
                return []

        except Exception as e:
            logger.error(f"Search execution error for query '{query}': {str(e)}")
            return []

    def analyze_search_result(self, result: Dict, phase: str, query: str) -> ResearchResult:
        """Analyze a search result for relevance and extract key insights"""

        class ResultAnalysis(BaseModel):
            title: str = ""
            relevance_score: float = Field(..., description="Score 0-1 indicating relevance to the research intent")
            credibility_score: float = Field(..., description="Score 0-1 indicating credibility of the source")
            key_insights: List[str] = Field(..., description="Key insights from this result relevant to the research")
            extracted_entities: Dict[str, List[str]] = Field(..., description="Entities extracted from the content")

        system_prompt = f"""
        You are a research content analyzer. Analyze this search result for relevance to our research intent
        and extract key insights.

        Research phase: {phase}
        Search query: {query}

        Research intent:
        - Domain: {self.intent.domain}
        - Intent type: {self.intent.intent_type}
        - Key entities: {", ".join(self.intent.key_entities)}

        IMPORTANT: Rate relevance strictly based on how well the content addresses the key entities and intent.
        For technical topics, evaluate based on the quality of technical information.

        Analyze for:
        1. Title of the content if available
        2. Relevance to our research intent (0-1 score)
        3. Credibility of the source (0-1 score)
        4. 3-5 key insights relevant to our research
        5. Entities mentioned related to our key research entities
        """

        logger.info(f"Analyzing search result from URL: {result['url']} for phase: {phase}")
        try:
            analysis = self._llm_call(
                system_prompt=system_prompt,
                prompt=result["content"][:8000],  # Limit content length
                response_format=ResultAnalysis
            )
            logger.info(f"Analysis result: {analysis}")

            # Update learning context based on analysis
            if analysis.relevance_score > 0.7:
                # Track successful search terms
                query_terms = query.lower().split()
                for term in query_terms:
                    if len(term) > 3:  # Only track meaningful terms
                        self.learning_context["successful_terms"][term] += 1
                logger.info(f"Updated learning context with successful terms: {query_terms}")

                # Track mentioned entities
                for entity_list in analysis.extracted_entities.values():
                    for entity in entity_list:
                        self.learning_context["entity_mentions"][entity] += 1
                logger.info(f"Updated entity mentions in learning context: {analysis.extracted_entities}")

                # Track source relevance
                domain = re.search(r"https?://(?:www\.)?([^/]+)", result["url"])
                if domain:
                    self.learning_context["relevance_by_source"][domain.group(1)].append(analysis.relevance_score)
                    logger.info(f"Tracked source relevance for domain: {domain.group(1)}")

            return ResearchResult(
                url=result["url"],
                title=analysis.title,
                content=result["content"][:1000],  # Store truncated content
                relevance_score=analysis.relevance_score,
                credibility_score=analysis.credibility_score,
                phase=phase,
                key_insights=analysis.key_insights,
                extracted_entities=analysis.extracted_entities,
                search_query=query
            )
        except Exception as e:
            logger.error(f"Error analyzing search result: {str(e)}")
            # Return a minimal result
            return ResearchResult(
                url=result["url"],
                content=result["content"][:500],
                relevance_score=0.1,
                credibility_score=0.1,
                phase=phase,
                search_query=query
            )

    def summarize_phase_results(self, phase: str) -> Dict:
        """Summarize results from the current research phase"""
        # Filter results for current phase
        phase_results = [r for r in self.research_results if r.phase == phase]
        logger.info(f"Summarizing results for phase: {phase}, {len(phase_results)} results found.")

        if not phase_results:
            logger.info(f"No results found for phase: {phase}")
            return {
                "phase": phase,
                "findings": [],
                "status": "no_results",
                "confidence_level": 0.0
            }

        class PhaseSummary(BaseModel):
            key_findings: List[str] = Field(..., description="Key findings from this research phase")
            entity_insights: Dict[str, List[str]] = Field(..., description="Insights organized by key entities")
            confidence_level: float = Field(..., description="Overall confidence in findings (0-1)")
            next_steps: List[str] = Field(..., description="Recommended next steps for research")
            knowledge_gaps: List[str] = Field(..., description="Areas where more information is needed")

        # Prepare context for the LLM
        context = {
            "phase": phase,
            "intent": self.intent.model_dump() if hasattr(self.intent, "model_dump") else self.intent.dict(),
            "results_count": len(phase_results),
            "top_insights": [
                {"url": r.url, "title": r.title, "insights": r.key_insights, "query": r.search_query}
                for r in sorted(phase_results, key=lambda x: x.relevance_score, reverse=True)[:5]
            ],
            "geo_context": self.geo_context
        }
        logger.info(f"Context for phase summary: {context}")

        system_prompt = f"""
        You are a research synthesis expert. Summarize the findings from the {phase} phase of research.

        Research intent:
        - Domain: {self.intent.domain}
        - Intent type: {self.intent.intent_type}
        - Key entities: {", ".join(self.intent.key_entities)}

        Create a synthesis that includes:
        1. Key findings from this phase (concise and non-redundant)
        2. Insights organized by key entities
        3. Confidence level in these findings (0-1)
        4. Recommended next steps
        5. Knowledge gaps that still need to be addressed

        Base your summary only on the search results provided, without introducing external information.
        """

        try:
            logger.info(f"Generating summary for phase: {phase}")
            summary = self._llm_call(
                system_prompt=system_prompt,
                prompt=json.dumps(context),
                response_format=PhaseSummary
            )
            logger.info(f"Generated phase summary: {summary}")

            result = {
                "phase": phase,
                "key_findings": summary.key_findings,
                "entity_insights": summary.entity_insights,
                "confidence_level": summary.confidence_level,
                "next_steps": summary.next_steps,
                "knowledge_gaps": summary.knowledge_gaps,
                "status": "completed"
            }

            self.phase_summaries[phase] = result
            logger.info(f"Phase summary saved: {result}")
            return result

        except Exception as e:
            logger.error(f"Error summarizing phase results: {str(e)}")
            # Return a minimal summary
            return {
                "phase": phase,
                "key_findings": ["Error generating summary"],
                "confidence_level": 0.1,
                "status": "error"
            }

    def should_advance_phase(self) -> bool:
        """Determine if research should advance to the next phase with improved criteria"""
        current_phase = self.current_phase
        iterations = self.phase_iterations[current_phase]
        logger.info(f"Checking if should advance from phase: {current_phase}, iteration: {iterations}")

        # If we've reached max iterations for this phase, advance
        if iterations >= self.max_iterations_per_phase[current_phase]:
            logger.info(f"Reached maximum iterations for {current_phase} phase, advancing")
            return True

        if current_phase == "discovery":
            # Advance if we have enough information from the discovery phase
            if self.phase_summaries.get("discovery"):
                confidence = self.phase_summaries["discovery"].get("confidence_level", 0)
                knowledge_gaps = self.phase_summaries["discovery"].get("knowledge_gaps", [])

                # If high confidence and few knowledge gaps, advance
                if confidence >= 0.85 and len(knowledge_gaps) <= 1:
                    logger.info(
                        f"Discovery phase reached sufficient confidence ({confidence}) with few knowledge gaps ({len(knowledge_gaps)})")
                    for gapid, gap in enumerate(knowledge_gaps, 1):
                        logger.info(
                            f'{gapid}. {gap}'
                        )
                    return True

                # If moderate confidence but many iterations, advance
                if confidence >= 0.6 and iterations >= 5:
                    logger.info(f"Discovery phase has moderate confidence ({confidence}) after {iterations} iterations")
                    return True

            return False

        elif current_phase == "focused":
            # Check if we have sufficient findings for key entities
            if self.phase_summaries.get("focused"):
                confidence = self.phase_summaries["focused"].get("confidence_level", 0)
                entity_insights = self.phase_summaries["focused"].get("entity_insights", {})

                # Count how many entities have at least 2 insights
                entities_with_insights = sum(1 for insights in entity_insights.values() if len(insights) >= 2)
                entities_coverage = entities_with_insights / len(
                    self.intent.key_entities) if self.intent.key_entities else 0

                # If good coverage and confidence, advance
                if confidence >= 0.65 and entities_coverage >= 0.7:
                    logger.info(
                        f"Focused phase has good entity coverage ({entities_coverage:.2f}) and confidence ({confidence})")
                    return True

                # If moderate confidence after multiple iterations, advance
                if confidence >= 0.6 and iterations >= 2:
                    logger.info(
                        f"Focused phase has moderate confidence ({confidence:.2f}) after {iterations} iteration")
                    return True

            return False

        elif current_phase == "validation":
            # Validate findings by checking confidence level
            if self.phase_summaries.get("validation"):
                confidence = self.phase_summaries["validation"].get("confidence_level", 0)

                # If high confidence or sufficient iterations, advance
                if confidence >= 0.7 or iterations >= 1:
                    logger.info(
                        f"Validation phase has sufficient confidence ({confidence:.2f}) or iterations ({iterations}), advancing.")
                    return True

            logger.info("Validation phase did not meet criteria to advance.")
            return iterations >= 1  # Always advance after at least one validation iteration

        elif current_phase == "comparison":
            # For comparison, we focus on getting comprehensive results
            if self.phase_summaries.get("comparison"):
                confidence = self.phase_summaries["comparison"].get("confidence_level", 0)
                findings_count = len(self.phase_summaries["comparison"].get("key_findings", []))

                # If high confidence and many findings, consider research complete
                if confidence >= 0.8 and findings_count >= 5:
                    logger.info(
                        f"Comparison phase has high confidence ({confidence}) and sufficient findings ({findings_count})")
                    return True

                # After several iterations with moderate confidence, also complete
                if confidence >= 0.7 and iterations >= 3:
                    logger.info(
                        f"Comparison phase has moderate confidence ({confidence}) after {iterations} iterations")
                    return True

                # If many iterations with limited new insights, also complete
                if iterations >= 5:
                    logger.info(f"Comparison phase has reached maximum iterations ({iterations}).")
                    return True
            logger.info("Comparison phase did not meet criteria to advance.")
            return False

        return False

    def advance_phase(self):
        """Advance to the next research phase"""
        phase_order = ["discovery", "focused", "validation", "comparison"]
        current_index = phase_order.index(self.current_phase)
        current_phase = self.current_phase  # Store current phase for later use

        # Determine the next phase before changing self.current_phase
        if current_index < len(phase_order) - 1:
            next_phase = phase_order[current_index + 1]
        else:
            next_phase = "completed"

        if current_index < len(phase_order) - 1:
            self.current_phase = phase_order[current_index + 1]
            logger.info(f"Advanced to {self.current_phase} phase")
        else:
            self.current_phase = "completed"
            logger.info("Research process completed")

        # If we're transitioning from focused phase, perform deep focus analysis
        # This happens regardless of why we're advancing (regular criteria or max iterations)
        if current_phase == "focused" and next_phase in ["validation", "completed"]:
            logger.info("Focus phase complete. Performing deep focus analysis before continuing.")
            try:
                # We need to access deep_focus_k which is passed to conduct_research
                # Let's make it an instance variable so we can access it here
                if hasattr(self, 'deep_focus_k'):
                    self._perform_deep_focus_analysis(self.deep_focus_k)
                else:
                    logger.warning("Unable to perform deep focus analysis: deep_focus_k not set")
            except Exception as e:
                logger.error(f"Error in deep focus analysis: {str(e)}")

    def generate_final_report(self) -> Dict:
        """Generate a comprehensive user-focused research report"""

        # Collect research context
        context = {
            "query": self.original_query,  # We'll need to add this attribute to store the original query
            "intent": self.intent.model_dump() if hasattr(self.intent, "model_dump") else self.intent.dict(),
            "phase_summaries": self.phase_summaries,
            "research_results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "phase": r.phase,
                    "key_insights": r.key_insights,
                    "relevance_score": r.relevance_score,
                    "credibility_score": r.credibility_score
                }
                for r in sorted(self.research_results, key=lambda x: x.relevance_score, reverse=True)
                if r.relevance_score > 0.5
            ],
        }

        # 2. Intent analysis section
        intent_section = self._generate_intent_section(context["intent"])

        # 3. Direct answer in points (executive summary)
        direct_answer = self._generate_direct_answer(context)

        # 4. Comprehensive knowledge summary
        knowledge_summary = self._generate_knowledge_summary(context)

        # 5. Generate tables for structured data
        tables = self._generate_tables(context)

        # 6. Relevant sources
        sources = self._generate_sources_section(context["research_results"])

        deep_focus_content = self._generate_deep_focus_section()

        # Combine all sections into a final report
        report = {
            "intent_analysis": intent_section,
            "direct_answer": direct_answer,
            "knowledge_summary": knowledge_summary,
            "deep_focus_insights": deep_focus_content,  # Add the new section
            "tables": tables,
            "sources": sources
        }

        return report

    def _generate_deep_focus_section(self) -> Dict:
        """Generate a section with deep focus insights if available"""
        if not hasattr(self, 'deep_focus_insights') or not self.deep_focus_insights:
            return {}

        # Get top URLs for deep focus insights
        deep_focus_urls = list(self.deep_focus_insights.keys())

        deep_focus_content = {
            "description": "In-depth analysis of highly relevant sources that appeared multiple times in research",
            "urls_analyzed": len(deep_focus_urls),
            "insights": {}
        }

        for url in deep_focus_urls:
            # Get URL title from research results
            title = "Source Analysis"  # Default to a better title

            # Try to extract domain name for a more meaningful title
            domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
            if domain_match:
                domain = domain_match.group(1)
                title = f"Analysis of {domain}"

            # Look for a better title in research results
            for result in self.research_results:
                if result.url == url and result.title and len(result.title) > 5 and result.title != "20 products":
                    # Only use if it's a meaningful title (not "20 products" or similar)
                    title = result.title
                    break

            # Extract key facts and analysis from deep insights
            key_facts = []
            entity_relationships = {}

            for insight in self.deep_focus_insights[url]:
                key_facts.extend(insight.key_facts)

                # Merge entity relationships
                for entity, relations in insight.entity_relationships.items():
                    if entity not in entity_relationships:
                        entity_relationships[entity] = []
                    entity_relationships[entity].extend(relations)

            # De-duplicate facts and relationships
            key_facts = list(set(key_facts))
            for entity in entity_relationships:
                entity_relationships[entity] = list(set(entity_relationships[entity]))

            deep_focus_content["insights"][url] = {
                "title": title,
                "key_facts": key_facts[:10],  # Limit to top 10 facts
                "entity_relationships": entity_relationships
            }

        return deep_focus_content

    def _generate_intent_section(self, intent: Dict) -> str:
        """Generate the intent analysis section"""
        system_prompt = """
        You are generating a research report section that explains the analysis of the research intent.
        Explain clearly how the research query was interpreted, including domain, intent type, key entities,
        and any constraints. Write in a clear, professional tone for the research requester.
        """

        return self._llm_call(
            system_prompt=system_prompt,
            prompt=json.dumps(intent),
            response_format=None
        )

    def _generate_direct_answer(self, context: Dict) -> str:
        """Generate a direct, concise answer to the query with URL verification"""
        system_prompt = """
        You are creating the executive summary section of a research report. 
        Based on the research findings, provide a direct, clear, and concise answer 
        to the original query. Present key points in a bulleted list format.

        Focus exclusively on answering the query without discussing methodology or research process.
        Use clear, factual statements.

        Incorporate deep focus insights when available - these are especially valuable as they come 
        from sources that appeared multiple times in research and received in-depth analysis."""

        key_findings = [
            finding for phase in context["phase_summaries"].values()
            if isinstance(phase, dict) and "key_findings" in phase
            for finding in phase.get("key_findings", [])
        ]

        # Get entity insights from phase summaries
        entity_insights = {
            k: v for phase in context["phase_summaries"].values()
            if isinstance(phase, dict) and "entity_insights" in phase
            for k, v in phase.get("entity_insights", {}).items()
        }

        # Add deep focus insights if available
        deep_focus_facts = []
        if hasattr(self, 'deep_focus_insights') and self.deep_focus_insights:
            for url, insights in self.deep_focus_insights.items():
                for insight in insights:
                    deep_focus_facts.extend(insight.key_facts)

        # Get the direct answer from LLM
        direct_answer = self._llm_call(
            system_prompt=system_prompt,
            prompt=json.dumps({
                "query": context["query"],
                "key_findings": key_findings,
                "entity_insights": entity_insights,
                "deep_focus_facts": deep_focus_facts  # Add deep focus facts
            }),
            response_format=None
        )

        # Initialize WordLlama for similarity matching if not already initialized
        if not hasattr(self, 'wordllama'):
            try:
                from wordllama import WordLlama
                self.wordllama = WordLlama.load()
                logger.info("WordLlama initialized for URL verification")
            except ImportError:
                logger.warning("WordLlama not available. URL verification will be skipped.")
                self.wordllama = None

        # If WordLlama is available, correct URLs in the direct answer
        if hasattr(self, 'wordllama') and self.wordllama:
            # Get all actual URLs from research results
            actual_urls = []
            for result in context["research_results"]:
                actual_urls.append({
                    "url": result["url"],
                    "title": result["title"]
                })

            # Find and replace URLs in the direct answer
            import re
            # Find URL pattern in the text
            url_pattern = r'\bhttps?://\S+\b|\[.*?\]\((https?://\S+)\)'

            def replace_url(match):
                matched_url = match.group(0)

                # If it's a Markdown link, extract the URL
                if matched_url.startswith('['):
                    # Extract title and URL from markdown link
                    md_match = re.match(r'\[(.*?)\]\((https?://\S+)\)', matched_url)
                    if md_match:
                        link_text = md_match.group(1)
                        url = md_match.group(2)

                        # Find the most similar actual URL using WordLlama
                        best_match = None
                        highest_score = -1
                        for actual in actual_urls:
                            # Compare URL similarity
                            url_score = self.wordllama.similarity(url, actual["url"])
                            # Compare title similarity if we have a link text
                            title_score = self.wordllama.similarity(link_text, actual["title"]) if actual[
                                "title"] else 0
                            # Take the average of URL and title similarity
                            combined_score = (url_score + title_score) / 2 if actual["title"] else url_score

                            if combined_score > highest_score:
                                highest_score = combined_score
                                best_match = actual

                        # Replace with the best matching URL if found
                        if best_match and highest_score > 0.3:  # Threshold for similarity
                            logger.info(f"Replacing URL {url} with {best_match['url']}")
                            return f"[{link_text}]({best_match['url']})"
                        return matched_url
                else:
                    # Plain URL case
                    url = matched_url

                    # Find the most similar actual URL
                    best_match = None
                    highest_score = -1
                    for actual in actual_urls:
                        score = self.wordllama.similarity(url, actual["url"])
                        if score > highest_score:
                            highest_score = score
                            best_match = actual

                    # Replace with the best matching URL if found
                    if best_match and highest_score > 0.3:  # Threshold for similarity
                        logger.info(f"Replacing URL {url} with {best_match['url']}")
                        if best_match["title"]:
                            return f"[{best_match['title']}]({best_match['url']})"
                        return best_match["url"]

                return matched_url

            # Replace all URLs in the direct answer
            direct_answer = re.sub(url_pattern, replace_url, direct_answer)

        return direct_answer

    def _generate_knowledge_summary(self, context: Dict) -> str:
        """Generate comprehensive knowledge summary"""
        system_prompt = """
        You are creating the comprehensive knowledge section of a research report.
        Synthesize all the research findings into a cohesive, well-structured narrative.

        Focus on:
        1. Organizing information logically by subtopics
        2. Explaining key concepts thoroughly
        3. Highlighting important relationships between concepts
        4. Addressing all aspects of the original query

        Write in a clear, professional academic style with proper paragraphing and structure.
        DO NOT discuss the research methodology or process - focus solely on the findings.
        """

        # Collect all findings and insights across phases
        all_findings = []
        all_insights = {}

        for phase, summary in context["phase_summaries"].items():
            if isinstance(summary, dict):
                if "key_findings" in summary:
                    all_findings.extend(summary["key_findings"])

                if "entity_insights" in summary:
                    for entity, insights in summary["entity_insights"].items():
                        if entity not in all_insights:
                            all_insights[entity] = []
                        all_insights[entity].extend(insights)

        knowledge_context = {
            "query": context["query"],
            "all_findings": all_findings,
            "all_insights": all_insights,
            "key_entities": context["intent"]["key_entities"],
        }

        return self._llm_call(
            system_prompt=system_prompt,
            prompt=json.dumps(knowledge_context),
            response_format=None
        )

    def _generate_tables(self, context: Dict) -> Dict:
        """Generate content-rich tables that organize research findings effectively"""

        # Define models for table structure
        class TableSpec(BaseModel):
            table_name: str = Field(..., description="A descriptive name for the table")
            description: str = Field(..., description="What information the table will present")
            columns: List[str] = Field(..., description="Column names for the table")
            data_type: List[str] = Field(..., description="Python data types for each column")

        class TableRecommendation(BaseModel):
            tables: List[TableSpec] = Field(..., description="List of recommended tables")

        # Extract all findings and insights from the research
        all_findings = []
        entity_insights = {}

        for phase, summary in context["phase_summaries"].items():
            if isinstance(summary, dict):
                if "key_findings" in summary:
                    all_findings.extend(summary["key_findings"])

                if "entity_insights" in summary:
                    for entity, insights in summary["entity_insights"].items():
                        if entity not in entity_insights:
                            entity_insights[entity] = []
                        entity_insights[entity].extend(insights)

        # Determine appropriate tables based on research domain and findings
        system_prompt = """
        You are creating information-rich tables for a research report. These tables should organize the research 
        findings in a way that makes them easy to understand and reference.

        Based on the research query, domain, and findings, recommend 2-3 tables that would best organize 
        and present the key information discovered. The tables should:

        1. Focus on organizing ACTUAL CONTENT from the findings, not just ratings
        2. Present information as a researcher would in their own notes or spreadsheet
        3. Be specific to the research domain and findings
        4. Help the reader quickly understand key information through structured organization

        For each table, specify:
        - table_name: A clear, descriptive name
        - description: What information the table presents and why it's useful
        - columns: Column names that organize the information logically
        - data_type: Data types for each column (typically "str" for most content)

        Consider what type of information organization would be most helpful:
        - Comparing different techniques, methods, or approaches
        - Categorizing findings by type, mechanism, or application
        - Summarizing key research contributions or papers
        - Organizing theoretical concepts and their practical applications

        Make sure columns and data_type lists are the same length.
        """

        try:
            # Get table recommendations based on the research content
            table_recs = self._llm_call(
                system_prompt=system_prompt,
                prompt=json.dumps({
                    "query": context["query"],
                    "domain": context["intent"]["domain"],
                    "intent_type": context["intent"]["intent_type"],
                    "key_entities": context["intent"]["key_entities"],
                    "key_findings_sample": all_findings[:10],
                    "entity_insights_sample": {k: v[:3] for k, v in entity_insights.items()},
                }),
                response_format=TableRecommendation
            )

            logger.info(f"Table recommendations received: {len(table_recs.tables)} tables")
            tables = {}

            # Process each recommended table
            for table_spec in table_recs.tables:
                try:
                    # Validate column and data type information
                    if not all(
                        k in table_spec.model_dump() for k in ["table_name", "description", "columns", "data_type"]):
                        logger.warning(f"Incomplete table specification, skipping")
                        continue

                    if len(table_spec.columns) != len(table_spec.data_type):
                        logger.warning(f"Column/datatype length mismatch, adjusting...")
                        min_len = min(len(table_spec.columns), len(table_spec.data_type))
                        table_spec.columns = table_spec.columns[:min_len]
                        table_spec.data_type = table_spec.data_type[:min_len]

                    # Create a dynamic model for the table rows
                    field_dict = {}
                    for col, dtype in zip(table_spec.columns, table_spec.data_type):
                        col_name = re.sub(r'[^a-zA-Z0-9]', '_', col.lower())
                        field_dict[col_name] = (str, Field(..., description=f"{col} content"))

                    DynamicTableModel = create_model(
                        f"Table_{re.sub(r'[^a-zA-Z0-9]', '', table_spec.table_name)}",
                        **field_dict
                    )

                    class TableData(BaseModel):
                        rows: List[DynamicTableModel] = Field(..., description=f"Data rows for {table_spec.table_name}")

                    # Generate the actual table content
                    data_prompt = f"""
                    You are filling in a research table with factual, specific information from the research findings.

                    Table: {table_spec.table_name}
                    Description: {table_spec.description}
                    Columns: {', '.join(table_spec.columns)}

                    IMPORTANT GUIDELINES:
                    1. Extract ACTUAL CONTENT from the research findings to fill each row
                    2. Be specific and detailed - include names, descriptions, and concrete information
                    3. Only include information supported by the research findings
                    4. Create 5-8 rows of well-organized, informative content
                    5. Make sure each cell contains meaningful information that would help a researcher

                    The table should help the reader quickly understand and reference key information about {context["query"]}.
                    """

                    table_data = self._llm_call(
                        system_prompt=data_prompt,
                        prompt=json.dumps({
                            "query": context["query"],
                            "all_findings": all_findings,
                            "entity_insights": entity_insights,
                            "top_results": [
                                {
                                    "title": r["title"],
                                    "key_insights": r["key_insights"],
                                    "url": r["url"]
                                }
                                for r in sorted(context["research_results"],
                                                key=lambda x: x["relevance_score"],
                                                reverse=True)[:8]
                                if r["relevance_score"] > 0.6
                            ]
                        }),
                        response_format=TableData
                    )

                    # Process the rows to use the original column names
                    column_key_map = {re.sub(r'[^a-zA-Z0-9]', '_', col.lower()): col for col in table_spec.columns}
                    processed_rows = []

                    for row in table_data.rows:
                        row_dict = row.model_dump() if hasattr(row, "model_dump") else row.dict()
                        processed_row = {}

                        for sanitized_key, original_key in column_key_map.items():
                            processed_row[original_key] = row_dict.get(sanitized_key, "")

                        processed_rows.append(processed_row)

                    tables[table_spec.table_name] = {
                        "description": table_spec.description,
                        "columns": table_spec.columns,
                        "data": processed_rows
                    }

                    logger.info(
                        f"Successfully generated table: {table_spec.table_name} with {len(processed_rows)} rows")

                except Exception as e:
                    logger.error(f"Error generating table {table_spec.table_name}: {str(e)}")

            # If no tables were generated, create a basic findings table
            if not tables and all_findings:
                try:
                    logger.info("No tables were successfully generated, creating a basic findings table")

                    domain = context["intent"]["domain"]
                    entity = context["intent"]["key_entities"][0] if context["intent"]["key_entities"] else "Findings"

                    tables["Key Research Findings"] = {
                        "description": f"Summary of main research findings about {entity}",
                        "columns": ["Finding", "Category", "Relevance", "Source"],
                        "data": [
                            {
                                "Finding": finding[:300] + ("..." if len(finding) > 300 else ""),
                                "Category": self._categorize_finding(finding, context["intent"]["key_entities"]),
                                "Relevance": "High" if i < 3 else "Medium" if i < 6 else "Supportive",
                                "Source": "Research Analysis"
                            }
                            for i, finding in enumerate(all_findings[:8])
                        ]
                    }

                    logger.info("Successfully created fallback findings table")

                except Exception as e:
                    logger.error(f"Error creating fallback table: {str(e)}")

            return tables

        except Exception as e:
            logger.error(f"Error in overall table generation: {str(e)}")
            return {}

    def _categorize_finding(self, finding, key_entities):
        """Categorize a finding based on its content and key entities"""
        finding_lower = finding.lower()

        categories = [
            "Methodology", "Technique", "Approach", "Framework",
            "Implementation", "Theory", "Application", "Comparison",
            "Limitation", "Advantage", "Case Study", "Analysis"
        ]

        # Try to match with key entities first
        for entity in key_entities:
            if entity.lower() in finding_lower:
                return entity

        # Look for category words
        for category in categories:
            if category.lower() in finding_lower:
                return category

        # Default categorization
        return "General Finding"

    def _generate_sources_section(self, research_results: List[Dict]) -> Dict:
        """Generate a section with relevant sources"""

        # Sort sources by relevance and credibility
        sorted_results = sorted(
            research_results,
            key=lambda x: (x["relevance_score"] + x["credibility_score"]),
            reverse=True
        )

        # Create a formatted list of sources
        sources = {
            "primary_sources": [
                {
                    "url": result["url"],
                    "title": result["title"],
                    "relevance_score": result["relevance_score"],
                    "key_insights": result["key_insights"][:2]  # Limit to top 2 insights per source
                }
                for result in sorted_results[:10]  # Top 10 sources
                if result["relevance_score"] >= 0.7
            ],
            "additional_sources": [
                {
                    "url": result["url"],
                    "title": result["title"]
                }
                for result in sorted_results[10:20]  # Next 10 sources
                if result["relevance_score"] >= 0.5
            ]
        }

        return sources

    def save_report_md(self, report: Dict, query: str, start_time, md_output_path):
        """Save the research report as a markdown file."""
        from datetime import datetime
        import os



        # Calculate research metrics
        total_sources = len(report['sources']['primary_sources']) + len(report['sources']['additional_sources'])
        total_processed_urls = len(self.processed_urls)
        total_queries = len(self.previous_queries)

        # Calculate phase durations
        total_iterations = sum(self.phase_iterations.values())

        # Calculate elapsed time
        research_duration = time.time() - start_time
        duration_min = int(research_duration // 60)
        duration_sec = int(research_duration % 60)

        # Generate markdown content with enhanced metrics header
        markdown_content = f"""# DeepResearch Report: {self.original_query}\n
| Research Metrics | Details |
|-----------------|---------|
| **Sources Used** | {total_sources} sources cited ({total_processed_urls} URLs processed) |
| **Search Queries** | {total_queries} unique queries executed |
| **Execution Time** | {duration_min}m {duration_sec}s ({research_duration:.1f} seconds) |
| **Generated** | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |

\n## Research Intent Analysis\n{report['intent_analysis']}

\n## Key Findings\n{report['direct_answer']}

\n## Comprehensive Analysis\n{report['knowledge_summary']}\n

            """

        if report.get('deep_focus_insights'):
            markdown_content += "\n## Deep Focus Analysis\n\n"
            # markdown_content += f"{report['deep_focus_insights']['description']}\n\n"

            for url, insight in report['deep_focus_insights']['insights'].items():
                markdown_content += f"### {insight['title']}\n"
                markdown_content += f"**Source:** [{url}]({url})\n\n"

                markdown_content += "#### Key Facts\n"
                for fact in insight['key_facts']:
                    markdown_content += f"- {fact}\n"

                markdown_content += "\n#### Entity Relationships\n"
                for entity, relationships in insight['entity_relationships'].items():
                    markdown_content += f"**{entity}**:\n"
                    for relation in relationships[:5]:  # Limit to top 5 relationships
                        markdown_content += f"- {relation}\n"
                markdown_content += "\n"

        # Add tables section if there are tables
        if report.get('tables'):
            markdown_content += "\n## Data Tables\n\n"
            for table_name, table_data in report['tables'].items():
                markdown_content += f"### {table_name}\n\n"
                markdown_content += f"{table_data['description']}\n\n"

                # Create table header
                markdown_content += "| " + " | ".join(table_data['columns']) + " |\n"
                markdown_content += "| " + " | ".join(["---"] * len(table_data['columns'])) + " |\n"

                # Add rows
                for row in table_data['data']:
                    markdown_content += "| " + " | ".join(
                        [str(row.get(col, "")) for col in table_data['columns']]) + " |\n"

                markdown_content += "\n\n"

        # Add sources section
        markdown_content += "\n## Sources\n\n"

        markdown_content += "### Primary Sources\n\n"
        for source in report['sources']['primary_sources']:
            markdown_content += f"- [{source['title']}]({source['url']})\n"
            if source.get('key_insights'):
                for insight in source['key_insights']:
                    markdown_content += f"  - {insight}\n"

        if report['sources']['additional_sources']:
            markdown_content += "\n### Additional Sources\n\n"
            for source in report['sources']['additional_sources']:
                markdown_content += f"- [{source['title']}]({source['url']})\n"


        if md_output_path:
            with open(md_output_path,'w') as f:
                f.write(markdown_content)
            logger.info(f"Report saved to {md_output_path}")


        return markdown_content

    def _generate_diverse_queries(self, num_queries: int = 3, retry_attempt: int = 0) -> List[SearchQuery]:
        """Generate more diverse search queries when initial ones return duplicate URLs"""

        # Get current focus for context
        focus = self.get_phase_focus()

        # Add stronger diversity instruction based on retry attempt
        diversity_instruction = f"""
        CRITICAL INSTRUCTION: Previous queries resulted in duplicate URLs.
        Generate completely new queries that will find UNIQUE content.

        Retry attempt: {retry_attempt} - Significantly increase diversity from previous queries.
        Previously processed URLs: {len(self.processed_urls)}

        Strategies to try:
        - Use different terminology or synonyms
        - Focus on different aspects of the research topic
        - Add specific qualifiers (year, methodology, application area)
        - Target specific authors or institutions if relevant
        - Adjust the scope (narrower or broader depending on results)
        """

        system_prompt = f"""
        You are a research query generator for a DeepResearch system. Generate {num_queries} search queries 
        that will help with research in the current phase.

        Current research phase: {self.current_phase}
        Phase goal: {focus["goal"]}
        Search strategy: {focus["search_strategy"]}
        Search priority: {focus["search_priority"]}

        Research intent:
        - Domain: {self.intent.domain}
        - Intent type: {self.intent.intent_type}
        - Temporal scope: {self.intent.temporal_scope}
        - Key entities: {", ".join(self.intent.key_entities)}

        {diversity_instruction}

        IMPORTANT: Focus exclusively on the key entities and research intent. 
        Generate queries that are:
        1. Specific and focused on finding information that matches the current phase
        2. HIGHLY diverse to avoid duplicate search results
        3. Formulated to discover new content not previously found
        4. Prioritized by importance (1 = highest priority, 5 = lowest)
        """

        logger.info(f"Generating {num_queries} diverse search queries for phase: {self.current_phase}")

        class QueryList(BaseModel):
            queries: List[SearchQuery]

        queries = self._llm_call(
            system_prompt=system_prompt,
            prompt="Generate diverse search queries that will find unique content for the current research phase.",
            response_format=QueryList
        )

        # Add to previous queries set
        for query in queries.queries:
            self.previous_queries.add(query.query)

        logger.info(f"Generated diverse queries: {queries}")
        return queries.queries

    def _perform_deep_focus_analysis(self, deep_focus_k):
        """Perform deeper analysis on frequently occurring URLs"""
        logger.info("Starting deep focus analysis on high-frequency URLs")

        # Get top N frequent URLs that we've processed
        most_common_urls = [url for url, _ in self.url_frequency.most_common(deep_focus_k)]

        if not most_common_urls:
            logger.info("No frequently occurring URLs found for deep focus")
            return

        logger.info(f"Performing deep focus on {len(most_common_urls)} most frequent URLs: {most_common_urls}")

        # Find the content for these URLs from our research results
        deep_focus_contents = {}
        for result in self.research_results:
            if result.url in most_common_urls:
                deep_focus_contents[result.url] = result.content

        # Only proceed if we have content to analyze
        if not deep_focus_contents:
            logger.info("No content found for frequent URLs in research results")
            return

        # Perform chunk-level deep analysis on each URL
        for url, content in deep_focus_contents.items():
            self._analyze_url_in_depth(url, content)

    def _analyze_url_in_depth(self, url, content):
        """Analyze a single URL's content in depth by chunking and detailed extraction"""
        logger.info(f"Deep analyzing URL: {url}")

        # Create a more focused model for in-depth extraction
        class DeepInsight(BaseModel):
            key_facts: List[str] = Field(..., description="Important facts extracted from this content chunk")
            detailed_analysis: str = Field(..., description="In-depth analysis of the content's significance")
            entity_relationships: Dict[str, List[str]] = Field(..., description="How entities relate to other concepts")
            connection_to_intent: float = Field(...,
                                                description="How strongly this connects to our research intent (0-1)")

        # Break content into chunks for more focused analysis
        # A simple approach is to split by paragraphs or sections
        chunks = self._chunk_content(content)
        logger.info(f"Split content into {len(chunks)} chunks for analysis")

        deep_insights = []

        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            system_prompt = f"""
            You are performing DEEP FOCUS analysis on content from a highly relevant source.
            This source has appeared multiple times in our research queries, indicating it's especially important.

            Analyze this content chunk in extreme detail, extracting:

            1. Key facts - specific, verifiable statements from the text
            2. Detailed analysis - deeper meaning and significance of this content
            3. Entity relationships - how concepts in this text connect to other relevant entities
            4. Connection to research intent - rate how strongly this connects to our research goal

            Research intent:
            - Domain: {self.intent.domain}
            - Intent type: {self.intent.intent_type}
            - Key entities: {", ".join(self.intent.key_entities)}

            Be extremely thorough and precise. This is a critical source for our research.
            """

            try:
                insight = self._llm_call(
                    system_prompt=system_prompt,
                    prompt=f"Content chunk {i + 1} from URL {url}:\n\n{chunk}",
                    response_format=DeepInsight
                )

                # Only keep insights with strong connection to our intent
                if insight.connection_to_intent >= 0.7:
                    deep_insights.append(insight)
                    logger.info(f"Added deep insight with connection strength: {insight.connection_to_intent}")

            except Exception as e:
                logger.error(f"Error analyzing chunk {i} from URL {url}: {str(e)}")

        # Store these deep insights for use in final report
        if url not in getattr(self, 'deep_focus_insights', {}):
            if not hasattr(self, 'deep_focus_insights'):
                self.deep_focus_insights = {}
            self.deep_focus_insights[url] = deep_insights

        logger.info(f"Completed deep analysis of {url}, extracted {len(deep_insights)} significant insights")

    def _chunk_content(self, content, max_chunk_size=1000, overlap=100):
        """Split content into overlapping chunks for detailed analysis"""
        if not content:
            return []

        # Simple chunking by size with overlap
        chunks = []
        content_length = len(content)

        for i in range(0, content_length, max_chunk_size - overlap):
            chunk_end = min(i + max_chunk_size, content_length)
            chunks.append(content[i:chunk_end])

            if chunk_end == content_length:
                break

        return chunks

    def conduct_research(self, query: str, max_urls, deep_focus_k, md_output_path) -> Dict:
        """Execute the full research process with improved control flow and error handling"""
        start_time = time.time()
        logger.info(f"Starting research on query: {query}")

        self.original_query = query
        self.url_frequency = Counter()  # Track how often each URL appears in search results
        self.deep_focus_k = deep_focus_k  # Store as instance variable

        self.analyze_intent(query)
        logger.info(
            f"Analyzed intent: {self.intent.domain}, {self.intent.intent_type}, geo_context: {self.intent.geo_context}")

        exit()

        # Initialize previous queries
        self.previous_queries = set()

        # Research phases loop
        while self.current_phase != "completed":
            phase_start_time = time.time()
            logger.info(
                f"\nExecuting {self.current_phase} phase, iteration {self.phase_iterations[self.current_phase] + 1}")

            try:
                # Generate search queries for current phase
                search_queries = self.generate_search_queries(num_queries=3)

                if not search_queries:
                    logger.warning(f"No valid search queries generated for {self.current_phase} phase")
                    self.phase_iterations[self.current_phase] += 1

                    if self.phase_iterations[self.current_phase] >= self.max_iterations_per_phase[
                        self.current_phase]:
                        logger.info(f"Max iterations reached for {self.current_phase}, advancing phase.")
                        self.advance_phase()
                    continue

                # Execute searches and analyze results
                phase_results = []
                retry_count = 0
                max_retries = 2  # Limit the number of query regeneration attempts

                while len(phase_results) < max_urls and retry_count <= max_retries:
                    for sq in search_queries:
                        logger.info(f"Searching: {sq.query}")

                        try:
                            # Execute search with timeout
                            results = self.execute_search(sq.query, max_urls)

                            for result in results:
                                try:
                                    analysis = self.analyze_search_result(result, self.current_phase, sq.query)
                                    self.research_results.append(analysis)
                                    phase_results.append(analysis)
                                except Exception as e:
                                    logger.error(f"Error analyzing result: {str(e)}")

                        except Exception as e:
                            logger.error(f"Error executing search for query '{sq.query}': {str(e)}")

                    # If we don't have enough unique results, regenerate queries
                    if len(phase_results) < max_urls and retry_count < max_retries:
                        logger.info(
                            f"Not enough unique URLs found ({len(phase_results)} < {max_urls}). Regenerating queries.")
                        retry_count += 1

                        # Generate more constrained queries with stronger emphasis on diversity
                        search_queries = self._generate_diverse_queries(num_queries=3, retry_attempt=retry_count)
                    else:
                        break

                # Check if we found any results
                if not phase_results:
                    logger.warning(
                        f"No results found in {self.current_phase} phase, iteration {self.phase_iterations[self.current_phase]}")

                    # Check if we should perform deep focus analysis after focused or validation phases
                if self.current_phase in ["focused", "validation"] and self.phase_iterations[
                    self.current_phase] >= 1:
                    self._perform_deep_focus_analysis(deep_focus_k)

                # Summarize phase results
                phase_summary = self.summarize_phase_results(self.current_phase)
                logger.info(f"Phase summary: {len(phase_summary.get('key_findings', []))} findings, " +
                            f"confidence: {phase_summary.get('confidence_level', 0):.2f}")

                # Update iteration count
                self.phase_iterations[self.current_phase] += 1

                # Check if we should advance to next phase
                if self.should_advance_phase():
                    logger.info(f"Advancing from {self.current_phase} to next phase")
                    self.advance_phase()

                # Log phase duration
                phase_duration = time.time() - phase_start_time
                logger.info(f"{self.current_phase} phase iteration completed in {phase_duration:.1f} seconds")

            except Exception as e:
                logger.error(f"Error in {self.current_phase} phase: {str(e)}")
                self.phase_iterations[self.current_phase] += 1

                if self.phase_iterations[self.current_phase] >= self.max_iterations_per_phase[self.current_phase]:
                    logger.warning(f"Moving to next phase after error in {self.current_phase}")
                    self.advance_phase()

        # Generate final report
        logger.info("Generating user-focused report")
        final_report = self.generate_final_report()
        logger.info("\nResearch completed. Final report generated.")

        # Save report to markdown file
        report_markdown = self.save_report_md(final_report, query, start_time,md_output_path)

        # Log total duration
        total_duration = time.time() - start_time
        logger.info(f"Total research duration: {total_duration:.1f} seconds")

        return final_report, report_markdown


# Example Usage
if __name__ == "__main__":


    # Configure max iterations for faster research
    # max_iterations = {
    #     "discovery": 2,
    #     "focused": 2,
    #     "validation": 1,
    #     "comparison": 3
    # }

    max_iterations = {
        "discovery": 1,
        "focused": 1,
        "validation": 1,
        "comparison": 1
    }
    max_urls = 1
    deep_focus_k = 1

    # max_iterations = {
    #     "discovery": 2,
    #     "focused": 2,
    #     "validation": 1,
    #     "comparison": 1
    # }
    # max_urls = 3
    # deep_focus_k = 2

    research_system = DeepResearchSystem(max_iterations_per_phase=max_iterations)

    # Example query
    query = "find the top 3 papers about beset adn latest chunkin using LLM, only arxiv papers."
    # query = "find best pebble watch ,i want under 3000 rupees, and with atleast 4.5 star review"
    # query = "find top two pebble watch ,i want under 2600 and 2900 rupees, and with atleast 4.5 star review"
    # query = "What are the best pebble watches under 3000 with 5 star reviews?"
    # query = "I want API documentaion of composio.dev Apps, Integrations, Actions, Tools"
    # query = "Find the top 5 papers about best and latest chunking technique using LLM , search on arxiv only okay."
    # query = "Find all the tokenizer techinques used in LLM,i want in order okay, atleast 5 to 10"
    # query = "What are the most promising techniques for reducing hallucinations in large language models?"
    # query = "What are the most effective machine learning algorithms for time series forecasting in financial markets?"

    # Conduct research
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
    filename = f"research_report_{safe_query}_{timestamp}.md"

    research_system.conduct_research(query, max_urls, deep_focus_k,filename)

    print("\n=== FINAL RESEARCH REPORT DONE ===")


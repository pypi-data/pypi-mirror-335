"""A structured proposal for academic paper development with core research elements."""

from typing import Dict, List

from fabricatio.models.generic import AsPrompt, CensoredAble, Display, PersistentAble, WithRef
from pydantic import Field


class ArticleProposal(CensoredAble, Display, WithRef[str], AsPrompt, PersistentAble):
    """Structured proposal for academic paper development with core research elements.

    Guides LLM in generating comprehensive research proposals with clearly defined components.
    """

    article_language: str
    """Written language of the article. SHALL be aligned to the language of the article briefing provided."""

    title: str = Field(...)
    """Paper title in academic style (Title Case, 8-15 words). Example: 'Exploring Neural Architecture Search for Low-Resource Machine Translation'"""

    focused_problem: List[str]
    """Specific research problem(s) or question(s) addressed (list of 1-3 concise statements).
    Example: ['NAS computational overhead in low-resource settings', 'Architecture transferability across language pairs']"""

    research_aim: List[str]
    """Primary research objectives (list of 2-4 measurable goals).
    Example: ['Develop parameter-efficient NAS framework', 'Establish cross-lingual architecture transfer metrics']"""

    research_methods: List[str]
    """Methodological components (list of techniques/tools).
    Example: ['Differentiable architecture search', 'Transformer-based search space', 'Multi-lingual perplexity evaluation']"""

    technical_approaches: List[str]
    """Technical approaches"""

    def _as_prompt_inner(self) -> Dict[str, str]:
        return {"ArticleBriefing": self.referenced, "ArticleProposal": self.display()}

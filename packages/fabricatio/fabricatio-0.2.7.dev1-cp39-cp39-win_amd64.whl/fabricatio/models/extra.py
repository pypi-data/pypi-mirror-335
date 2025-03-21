"""Extra models for built-in actions."""

from abc import abstractmethod
from itertools import chain
from typing import Dict, Generator, List, Optional, Self, Tuple, final

from fabricatio.journal import logger
from fabricatio.models.generic import AsPrompt, Base, CensoredAble, Display, PrepareVectorization, ProposedAble, WithRef
from fabricatio.models.utils import ok
from pydantic import BaseModel, Field

# <editor-fold desc="ArticleEssence">


class Equation(BaseModel):
    """Mathematical formalism specification for research contributions.

    Encodes equations with dual representation: semantic meaning and typeset-ready notation.
    """

    description: str
    """Equation significance structured in three elements:
    1. Physical/conceptual meaning of the equation.
    2. Role in technical workflow (e.g., derivation, optimization, or analysis).
    3. Relationship to the paper's core contribution (e.g., theoretical foundation, empirical validation).
    Example: "Defines constrained search space dimensionality reduction. Used in architecture optimization phase (Section 3.2). Enables 40% parameter reduction."
    """

    latex_code: str
    """LaTeX representation following academic typesetting standards:
    - Must use equation environment (e.g., `equation`, `align`).
    - Multiline equations must align at '=' using `&`.
    - Include unit annotations where applicable.
    Example: "\\begin{equation} \\mathcal{L}_{NAS} = \\alpha \\|\\theta\\|_2 + \\beta H(p) \\end{equation}"
    """


class Figure(BaseModel):
    """Visual component specification for technical communication.

    Combines graphical assets with structured academic captioning.Extracted from the article provided
    """

    description: str
    """Figure interpretation guide containing:
    1. Key visual elements mapping (e.g., axes, legends, annotations).
    2. Data representation methodology (e.g., visualization type, statistical measures).
    3. Connection to research findings (e.g., supports hypothesis, demonstrates performance).
    Example: "Architecture search space topology (left) vs. convergence curves (right). Demonstrates NAS efficiency gains through constrained search."
    """

    figure_caption: str
    """Complete caption following Nature-style guidelines:
    1. Brief overview statement (首句总结).
    2. Technical detail layer (e.g., data sources, experimental conditions).
    3. Result implication (e.g., key insights, implications for future work).
    Example: "Figure 3: Differentiable NAS framework. (a) Search space topology with constrained dimensions. (b) Training convergence across language pairs. Dashed lines indicate baseline methods."
    """

    figure_serial_number: int
    """The Image serial number extracted from the Markdown article provided, the path usually in the form of `![](images/1.jpg)`, in this case the serial number is `1`"""


class Algorithm(BaseModel):
    """Algorithm specification for research contributions."""

    title: str
    """Algorithm title with technical focus descriptor (e.g., 'Gradient Descent Optimization').

    Tip: Do not attempt to translate the original element titles when generating JSON.
    """

    description: str
    """Algorithm description with technical focus descriptor:
    - Includes input/output specifications.
    - Describes key steps and their purpose.
    - Explains its role in the research workflow.
    Example: "Proposed algorithm for neural architecture search. Inputs include search space constraints and training data. Outputs optimized architecture."
    """


class Table(BaseModel):
    """Table specification for research contributions."""

    title: str
    """Table title with technical focus descriptor (e.g., 'Comparison of Model Performance Metrics').

    Tip: Do not attempt to translate the original element titles when generating JSON.
    """

    description: str
    """Table description with technical focus descriptor:
    - Includes data source and structure.
    - Explains key columns/rows and their significance.
    - Connects to research findings or hypotheses.
    Example: "Performance metrics for different architectures. Columns represent accuracy, F1-score, and inference time. Highlights efficiency gains of proposed method."
    """


class Highlightings(BaseModel):
    """Technical showcase aggregator for research artifacts.

    Curates core scientific components with machine-parseable annotations.
    """

    highlighted_equations: List[Equation]
    """3-5 pivotal equations representing theoretical contributions:
    - Each equation must be wrapped in $$ for display math.
    - Contain at least one novel operator/symbol.
    - Be referenced in Methods/Results sections.
    Example: Equation describing proposed loss function.
    """

    highlighted_algorithms: List[Algorithm]
    """1-2 key algorithms demonstrating methodological contributions:
    - Include pseudocode or step-by-step descriptions.
    - Highlight innovation in computational approach.
    Example: Algorithm for constrained search space exploration.

    Tip: Do not attempt to translate the original element titles when generating JSON.
    """

    highlighted_figures: List[Figure]
    """4-6 key figures demonstrating:
    1. Framework overview (1 required).
    2. Quantitative results (2-3 required).
    3. Ablation studies (1 optional).
    Each must appear in Results/Discussion chapters.
    Example: Figure showing architecture topology and convergence curves.
    """

    highlighted_tables: List[Table]
    """2-3 key tables summarizing:
    - Comparative analysis of methods.
    - Empirical results supporting claims.
    Example: Table comparing model performance across datasets.

    Tip: Do not attempt to translate the original element titles when generating JSON.
    """


class ArticleEssence(ProposedAble, Display, PrepareVectorization):
    """Semantic fingerprint of academic paper for structured analysis.

    Encodes research artifacts with dual human-machine interpretability.
    """

    title: str = Field(...)
    """Exact title of the original article without any modification.
    Must be preserved precisely from the source material without:
    - Translation
    - Paraphrasing
    - Adding/removing words
    - Altering style or formatting
    """

    authors: List[str]
    """Original author names exactly as they appear in the source document. No translation or paraphrasing.
    Extract complete list without any modifications or formatting changes."""

    keywords: List[str]
    """Original keywords exactly as they appear in the source document. No translation or paraphrasing.
    Extract the complete set without modifying format or terminology."""

    publication_year: int
    """Publication timestamp in ISO 8601 (YYYY format)."""

    highlightings: Highlightings
    """Technical highlight reel containing:
    - Core equations (Theory)
    - Key algorithms (Implementation)
    - Critical figures (Results)
    - Benchmark tables (Evaluation)"""

    domain: List[str]
    """Domain tags for research focus."""

    abstract: str = Field(...)
    """Three-paragraph structured abstract:
    Paragraph 1: Problem & Motivation (2-3 sentences)
    Paragraph 2: Methodology & Innovations (3-4 sentences)
    Paragraph 3: Results & Impact (2-3 sentences)
    Total length: 150-250 words"""

    core_contributions: List[str]
    """3-5 technical contributions using CRediT taxonomy verbs.
    Each item starts with action verb.
    Example:
    - 'Developed constrained NAS framework'
    - 'Established cross-lingual transfer metrics'"""

    technical_novelty: List[str]
    """Patent-style claims with technical specificity.
    Format: 'A [system/method] comprising [novel components]...'
    Example:
    'A neural architecture search system comprising:
     a differentiable constrained search space;
     multi-lingual transferability predictors...'"""

    research_problems: List[str]
    """Problem statements as how/why questions.
    Example:
    - 'How to reduce NAS computational overhead while maintaining search diversity?'
    - 'Why do existing architectures fail in low-resource cross-lingual transfer?'"""

    limitations: List[str]
    """Technical limitations analysis containing:
    1. Constraint source (data/method/theory)
    2. Impact quantification
    3. Mitigation pathway
    Example:
    'Methodology constraint: Single-objective optimization (affects 5% edge cases),
    mitigated through future multi-task extension'"""

    future_work: List[str]
    """Research roadmap items with 3 horizons:
    1. Immediate extensions (1 year)
    2. Mid-term directions (2-3 years)
    3. Long-term vision (5+ years)
    Example:
    'Short-term: Adapt framework for vision transformers (ongoing with CVPR submission)'"""

    impact_analysis: List[str]
    """Bibliometric impact projections:
    - Expected citation counts (next 3 years)
    - Target application domains
    - Standard adoption potential
    Example:
    'Predicted 150+ citations via integration into MMEngine (Alibaba OpenMMLab)'"""

    def _prepare_vectorization_inner(self) -> str:
        return self.model_dump_json()


# </editor-fold>


class ArticleProposal(CensoredAble, Display, WithRef[str], AsPrompt):
    """Structured proposal for academic paper development with core research elements.

    Guides LLM in generating comprehensive research proposals with clearly defined components.
    """

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


class ArticleRef(CensoredAble):
    """Reference to a specific section or subsection within an article.

    Always instantiated with a fine-grind reference to a specific subsection if possible.
    """

    referred_chapter_title: str
    """Full title of the chapter that contains the referenced section."""

    referred_section_title: Optional[str] = None
    """Full title of the section that contains the referenced subsection. Defaults to None if not applicable, which means the reference is to the entire chapter."""

    referred_subsection_title: Optional[str] = None
    """Full title of the subsection that contains the referenced paragraph. Defaults to None if not applicable, which means the reference is to the entire section."""

    def __hash__(self) -> int:
        """Overrides the default hash function to ensure consistent hashing across instances."""
        return hash((self.referred_chapter_title, self.referred_section_title, self.referred_subsection_title))


# <editor-fold desc="ArticleOutline">
class ArticleOutlineBase(Base):
    """Atomic research component specification for academic paper generation."""

    writing_aim: List[str]
    """Required: List of specific rhetorical objectives (3-5 items).
    Format: Each item must be an actionable phrase starting with a verb.
    Example: ['Establish metric validity', 'Compare with baseline approaches',
             'Justify threshold selection']"""
    support_to: List[ArticleRef]
    """Required: List of ArticleRef objects identifying components this section provides evidence for.
    Format: Each reference must point to a specific chapter, section, or subsection.
    Note: References form a directed acyclic graph in the document structure."""

    depend_on: List[ArticleRef]
    """Required: List of ArticleRef objects identifying components this section builds upon.
    Format: Each reference must point to a previously defined chapter, section, or subsection.
    Note: Circular dependencies are not permitted."""

    description: str = Field(...)
    """Description of the research component in academic style."""
    title: str = Field(...)
    """Title of the research component in academic style."""


class ArticleSubsectionOutline(ArticleOutlineBase):
    """Atomic research component specification for academic paper generation."""


class ArticleSectionOutline(ArticleOutlineBase):
    """Methodological unit organizing related technical components."""

    subsections: List[ArticleSubsectionOutline] = Field(
        ...,
    )
    """IMRaD-compliant substructure with technical progression:
    1. Conceptual Framework
    2. Methodological Details
    3. Implementation Strategy
    4. Validation Approach
    5. Transition Logic

    Example Flow:
    [
        'Search Space Constraints',
        'Gradient Optimization Protocol',
        'Multi-GPU Implementation',
        'Convergence Validation',
        'Cross-Lingual Extension'
    ]"""


class ArticleChapterOutline(ArticleOutlineBase):
    """Macro-structural unit implementing standard academic paper organization."""

    sections: List[ArticleSectionOutline] = Field(
        ...,
    )
    """Standard academic progression implementing chapter goals:
    1. Context Establishment
    2. Technical Presentation
    3. Empirical Validation
    4. Comparative Analysis
    5. Synthesis

    Example Structure:
    [
        'Experimental Setup',
        'Monolingual Baselines',
        'Cross-Lingual Transfer',
        'Low-Resource Scaling',
        'Error Analysis'
    ]"""


class ArticleOutline(Display, CensoredAble, WithRef[ArticleProposal]):
    """Complete academic paper blueprint with hierarchical validation."""

    title: str = Field(...)
    """Full technical title following ACL 2024 guidelines:
    - Title Case with 12-18 word limit
    - Structure: [Method] for [Task] via [Approach] in [Domain]
    Example: 'Efficient Differentiable NAS for Low-Resource MT Through
    Parameter-Sharing: A Cross-Lingual Study'"""

    prospect: str = Field(...)
    """Consolidated research statement with four pillars:
    1. Problem Identification: Current limitations
    2. Methodological Response: Technical approach
    3. Empirical Validation: Evaluation strategy
    4. Scholarly Impact: Field contributions

    Example: 'Addressing NAS computational barriers through constrained
    differentiable search spaces, validated via cross-lingual MT experiments
    across 50+ languages, enabling efficient architecture discovery with
    60% reduced search costs.'"""

    chapters: List[ArticleChapterOutline]
    """IMRaD structure with enhanced academic validation:
    1. Introduction: Problem Space & Contributions
    2. Background: Theoretical Foundations
    3. Methods: Technical Innovations
    4. Experiments: Protocol Design
    5. Results: Empirical Findings
    6. Discussion: Interpretation & Limitations
    7. Conclusion: Synthesis & Future Work
    8. Appendices: Supplementary Materials"""

    abstract: str = Field(...)
    """The abstract is a concise summary of the academic paper's main findings."""

    def finalized_dump(self) -> str:
        """Generates standardized hierarchical markup for academic publishing systems.

        Implements ACL 2024 outline conventions with four-level structure:
        = Chapter Title (Level 1)
        == Section Title (Level 2)
        === Subsection Title (Level 3)
        ==== Subsubsection Title (Level 4)

        Returns:
            str: Strictly formatted outline with academic sectioning

        Example:
            = Methodology
            == Neural Architecture Search Framework
            === Differentiable Search Space
            ==== Constrained Optimization Parameters
            === Implementation Details
            == Evaluation Protocol
        """
        lines: List[str] = []
        for i, chapter in enumerate(self.chapters, 1):
            lines.append(f"= Chapter {i}: {chapter.title}")
            for j, section in enumerate(chapter.sections, 1):
                lines.append(f"== {i}.{j} {section.title}")
                for k, subsection in enumerate(section.subsections, 1):
                    lines.append(f"=== {i}.{j}.{k} {subsection.title}")
        return "\n".join(lines)


# </editor-fold>


# <editor-fold desc="Article">
class Paragraph(CensoredAble):
    """Structured academic paragraph blueprint for controlled content generation."""

    description: str
    """Functional summary of the paragraph's role in document structure.
    Example: 'Establishes NAS efficiency improvements through differentiable methods'"""

    writing_aim: List[str]
    """Specific communicative objectives for this paragraph's content.
    Example: ['Introduce gradient-based NAS', 'Compare computational costs',
             'Link efficiency to practical applications']"""

    sentences: List[str]
    """List of sentences forming the paragraph's content."""


class ArticleBase(CensoredAble, Display, ArticleOutlineBase):
    """Foundation for hierarchical document components with dependency tracking."""

    @abstractmethod
    def to_typst_code(self) -> str:
        """Converts the component into a Typst code snippet for rendering."""

    def _update_pre_check(self, other: Self) -> Self:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Cannot update from a non-{self.__class__} instance.")
        if self.title != other.title:
            raise ValueError("Cannot update from a different title.")

    @abstractmethod
    def _update_from_inner(self, other: Self) -> Self:
        """Updates the current instance with the attributes of another instance."""

    @final
    def update_from(self, other: Self) -> Self:
        """Updates the current instance with the attributes of another instance."""
        return self._update_pre_check(other)._update_from_inner(other)

    def __eq__(self, other: "ArticleBase") -> bool:
        """Compares two ArticleBase objects based on their model_dump_json representation."""
        return self.model_dump_json() == other.model_dump_json()

    def __hash__(self) -> int:
        """Calculates a hash value for the ArticleBase object based on its model_dump_json representation."""
        return hash(self.model_dump_json())


class ArticleSubsection(ArticleBase):
    """Atomic argumentative unit with technical specificity."""

    paragraphs: List[Paragraph]
    """List of Paragraph objects containing the content of the subsection."""

    def _update_from_inner(self, other: Self) -> Self:
        """Updates the current instance with the attributes of another instance."""
        logger.debug(f"Updating SubSection {self.title}")
        self.paragraphs = other.paragraphs
        return self

    def to_typst_code(self) -> str:
        """Converts the component into a Typst code snippet for rendering.

        Returns:
            str: Typst code snippet for rendering.
        """
        return f"=== {self.title}\n" + "\n\n".join("".join(p.sentences) for p in self.paragraphs)


class ArticleSection(ArticleBase):
    """Atomic argumentative unit with high-level specificity."""

    subsections: List[ArticleSubsection]

    def _update_from_inner(self, other: Self) -> Self:
        """Updates the current instance with the attributes of another instance."""
        for self_subsec, other_subsec in zip(self.subsections, other.subsections, strict=True):
            self_subsec.update_from(other_subsec)
        return self

    def to_typst_code(self) -> str:
        """Converts the section into a Typst formatted code snippet.

        Returns:
            str: The formatted Typst code snippet.
        """
        return f"== {self.title}\n" + "\n\n".join(subsec.to_typst_code() for subsec in self.subsections)


class ArticleChapter(ArticleBase):
    """Thematic progression implementing research function."""

    sections: List[ArticleSection]
    """Thematic progression implementing chapter's research function."""

    def _update_from_inner(self, other: Self) -> Self:
        """Updates the current instance with the attributes of another instance."""
        for self_sec, other_sec in zip(self.sections, other.sections, strict=True):
            self_sec.update_from(other_sec)
        return self

    def to_typst_code(self) -> str:
        """Converts the chapter into a Typst formatted code snippet for rendering."""
        return f"= {self.title}\n" + "\n\n".join(sec.to_typst_code() for sec in self.sections)


class Article(Display, CensoredAble, WithRef[ArticleOutline]):
    """Complete academic paper specification with validation constraints."""

    title: str = Field(...)
    """The academic title"""

    abstract: str = Field(...)
    """Abstract of the academic paper."""

    chapters: List[ArticleChapter]
    """List of ArticleChapter objects representing the academic paper's structure."""

    def finalized_dump(self) -> str:
        """Exports the article in `typst` format.

        Returns:
                str: Strictly formatted outline with typst formatting.
        """
        return "\n\n".join(c.to_typst_code() for c in self.chapters)

    @classmethod
    def from_outline(cls, outline: ArticleOutline) -> "Article":
        """Generates an article from the given outline.

        Args:
            outline (ArticleOutline): The outline to generate the article from.

        Returns:
            Article: The generated article.
        """
        # Set the title from the outline
        article = Article(**outline.model_dump(include={"title", "abstract"}), chapters=[])

        for chapter in outline.chapters:
            # Create a new chapter
            article_chapter = ArticleChapter(
                sections=[],
                **chapter.model_dump(exclude={"sections"}),
            )
            for section in chapter.sections:
                # Create a new section
                article_section = ArticleSection(
                    subsections=[],
                    **section.model_dump(exclude={"subsections"}),
                )
                for subsection in section.subsections:
                    # Create a new subsection
                    article_subsection = ArticleSubsection(
                        paragraphs=[],
                        **subsection.model_dump(),
                    )
                    article_section.subsections.append(article_subsection)
                article_chapter.sections.append(article_section)
            article.chapters.append(article_chapter)
        return article

    def chap_iter(self) -> Generator[ArticleChapter, None, None]:
        """Iterates over all chapters in the article.

        Yields:
            ArticleChapter: Each chapter in the article.
        """
        yield from self.chapters

    def section_iter(self) -> Generator[ArticleSection, None, None]:
        """Iterates over all sections in the article.

        Yields:
            ArticleSection: Each section in the article.
        """
        for chap in self.chapters:
            yield from chap.sections

    def subsection_iter(self) -> Generator[ArticleSubsection, None, None]:
        """Iterates over all subsections in the article.

        Yields:
            ArticleSubsection: Each subsection in the article.
        """
        for sec in self.section_iter():
            yield from sec.subsections

    def iter_dfs(self) -> Generator[ArticleBase, None, None]:
        """Performs a depth-first search (DFS) through the article structure.

        Returns:
            Generator[ArticleBase]: Each component in the article structure.
        """
        for chap in self.chap_iter():
            for sec in chap.sections:
                yield from sec.subsections
                yield sec
            yield chap

    def deref(self, ref: ArticleRef) -> ArticleBase:
        """Resolves a reference to the corresponding section or subsection in the article.

        Args:
            ref (ArticleRef): The reference to resolve.

        Returns:
            ArticleBase: The corresponding section or subsection.
        """
        chap = ok(
            next(chap for chap in self.chap_iter() if chap.title == ref.referred_chapter_title), "Chapter not found"
        )
        if ref.referred_section_title is None:
            return chap
        sec = ok(next(sec for sec in chap.sections if sec.title == ref.referred_section_title))
        if ref.referred_subsection_title is None:
            return sec
        return ok(next(subsec for subsec in sec.subsections if subsec.title == ref.referred_subsection_title))

    def gather_dependencies(self, article: ArticleBase) -> List[ArticleBase]:
        """Gathers dependencies for all sections and subsections in the article.

        This method should be called after the article is fully constructed.
        """
        depends = [self.deref(a) for a in article.depend_on]

        supports = []
        for a in self.iter_dfs():
            if article in {self.deref(b) for b in a.support_to}:
                supports.append(a)

        return list(set(depends + supports))

    def gather_dependencies_recursive(self, article: ArticleBase) -> List[ArticleBase]:
        """Gathers all dependencies recursively for the given article.

        Args:
            article (ArticleBase): The article to gather dependencies for.

        Returns:
            List[ArticleBase]: A list of all dependencies for the given article.
        """
        q = self.gather_dependencies(article)

        deps = []
        while a := q.pop():
            deps.extend(self.gather_dependencies(a))

        deps = list(
            chain(
                filter(lambda x: isinstance(x, ArticleChapter), deps),
                filter(lambda x: isinstance(x, ArticleSection), deps),
                filter(lambda x: isinstance(x, ArticleSubsection), deps),
            )
        )

        # Initialize result containers
        formatted_code = ""
        processed_components = []

        # Process all dependencies
        while component := deps.pop():
            # Skip duplicates
            if (component_code := component.to_typst_code()) in formatted_code:
                continue

            # Add this component
            formatted_code += component_code
            processed_components.append(component)

        return processed_components

    def iter_dfs_with_deps(self) -> Generator[Tuple[ArticleBase, List[ArticleBase]], None, None]:
        """Iterates through the article in a depth-first manner, yielding each component and its dependencies.

        Yields:
            Tuple[ArticleBase, List[ArticleBase]]: Each component and its dependencies.
        """
        for component in self.iter_dfs():
            yield component, (self.gather_dependencies_recursive(component))


# </editor-fold>

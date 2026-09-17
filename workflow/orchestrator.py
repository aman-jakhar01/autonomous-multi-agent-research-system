from langgraph.graph import StateGraph, END

from workflow.state import ResearchState

from agents.query_planner import generate_research_queries
from agents.research_agent import research_topic
from agents.analyst_agent import analyze_research
from agents.validator_agent import validate_claims
from agents.writer_agent import write_report


# ============================================================
# QUERY PLANNER NODE
# ============================================================

def query_planner_node(
    state: ResearchState
):

    print("\n" + "=" * 60)
    print("🧠 QUERY PLANNER")
    print("=" * 60)

    # --------------------------------------------------------
    # INITIAL RESEARCH
    # --------------------------------------------------------

    if state["research_round"] == 0:

        queries = generate_research_queries(
            topic=state["topic"],
            groq_api_key=state[
                "groq_api_key"
            ]
        )

    # --------------------------------------------------------
    # FOLLOW-UP RESEARCH
    # --------------------------------------------------------

    else:

        missing_information = (
            state["missing_information"]
        )

        queries = []

        print(
            "\n🎯 Creating targeted "
            "follow-up queries..."
        )

        for item in missing_information:

            query = (
                f"{state['topic']} "
                f"{item}"
            )

            queries.append(
                query
            )

            print(
                f"→ {query}"
            )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    if not queries:

        queries = [
            state["topic"]
        ]

    print(
        "\n📋 RESEARCH PLAN:"
    )

    for i, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"{i}. {query}"
        )

    return {
        "research_queries": queries
    }


# ============================================================
# RESEARCH NODE
# ============================================================

def research_node(
    state: ResearchState
):

    print("\n" + "=" * 60)
    print("🔎 RESEARCH AGENT")
    print("=" * 60)

    print(
        f"Research round: "
        f"{state['research_round'] + 1}"
    )

    queries = state[
        "research_queries"
    ]

    sources = research_topic(
        topic=state["topic"],
        queries=queries,
        tavily_api_key=state[
            "tavily_api_key"
        ]
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES FROM PREVIOUS ROUNDS
    # --------------------------------------------------------

    existing_sources = state[
        "sources"
    ]

    existing_urls = {
        source.url
        for source in existing_sources
    }

    new_sources = []

    for source in sources:

        if source.url in existing_urls:
            continue

        existing_urls.add(
            source.url
        )

        new_sources.append(
            source
        )

    all_sources = (
        existing_sources
        + new_sources
    )

    print(
        f"\nExisting sources: "
        f"{len(existing_sources)}"
    )

    print(
        f"New sources: "
        f"{len(new_sources)}"
    )

    print(
        f"Total unique sources: "
        f"{len(all_sources)}"
    )

    return {

        "sources": all_sources,

        "research_round":
            state["research_round"] + 1
    }


# ============================================================
# ANALYSIS NODE
# ============================================================

def analysis_node(
    state: ResearchState
):

    print("\n" + "=" * 60)
    print("📊 ANALYST AGENT")
    print("=" * 60)

    result = analyze_research(
        topic=state["topic"],
        sources=state["sources"],
        groq_api_key=state[
            "groq_api_key"
        ]
    )

    print(
        f"Needs more research: "
        f"{result.needs_more_research}"
    )

    print(
        f"Confidence: "
        f"{result.confidence_score}"
    )

    print(
        f"Claims generated: "
        f"{len(result.claims)}"
    )

    if result.missing_information:

        print(
            "\n🧠 Missing information:"
        )

        for item in (
            result.missing_information
        ):

            print(
                f"- {item}"
            )

    return {

        "analysis":
            result.analysis,

        "claims":
            result.claims,

        "needs_more_research":
            result.needs_more_research,

        "missing_information":
            result.missing_information,

        "confidence_score":
            result.confidence_score
    }


# ============================================================
# RESEARCH DECISION
# ============================================================

def research_decision(
    state: ResearchState
):

    if (
        state["needs_more_research"]
        and
        state["research_round"]
        < state["max_research_rounds"]
    ):

        print(
            "\n🔄 More research required."
        )

        return "planner"

    print(
        "\n✅ Research is sufficient."
    )

    return "validation"


# ============================================================
# VALIDATION NODE
# ============================================================

def validation_node(
    state: ResearchState
):

    print("\n" + "=" * 60)
    print("🔍 CITATION VALIDATOR")
    print("=" * 60)

    result = validate_claims(
        claims=state["claims"],
        sources=state["sources"],
        groq_api_key=state[
            "groq_api_key"
        ]
    )

    print(
        f"\nValidation: "
        f"{result.valid}"
    )

    print(
        f"Validation score: "
        f"{result.score:.2f}"
    )

    validation_issues = []

    if result.issues:

        print(
            "\n⚠️ VALIDATION ISSUES:"
        )

        for issue in result.issues:

            print(
                f"- "
                f"[{issue.severity.upper()}] "
                f"{issue.claim}"
            )

            print(
                f"  Reason: "
                f"{issue.reason}"
            )

            validation_issues.append(
                f"[{issue.severity}] "
                f"{issue.claim}: "
                f"{issue.reason}"
            )

    if result.conflicts:

        print(
            "\n⚔️ SOURCE CONFLICTS:"
        )

        for conflict in (
            result.conflicts
        ):

            print(
                f"- {conflict}"
            )

            validation_issues.append(
                f"[CONFLICT] "
                f"{conflict}"
            )

    return {

        "validation_score":
            result.score,

        "validation_issues":
            validation_issues
    }


# ============================================================
# WRITER NODE
# ============================================================

def writer_node(
    state: ResearchState
):

    print("\n" + "=" * 60)
    print("✍️ WRITER AGENT")
    print("=" * 60)

    report = write_report(

        topic=state["topic"],

        analysis=state["analysis"],

        claims=state["claims"],

        sources=state["sources"],

        groq_api_key=state[
            "groq_api_key"
        ]
    )

    print(
        "\n✅ Report generated."
    )

    return {
        "report": report
    }


# ============================================================
# BUILD WORKFLOW
# ============================================================

def build_workflow():

    graph = StateGraph(
        ResearchState
    )

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
        "planner",
        query_planner_node
    )

    graph.add_node(
        "research",
        research_node
    )

    graph.add_node(
        "analysis",
        analysis_node
    )

    graph.add_node(
        "validation",
        validation_node
    )

    graph.add_node(
        "writer",
        writer_node
    )

    # --------------------------------------------------------
    # ENTRY
    # --------------------------------------------------------

    graph.set_entry_point(
        "planner"
    )

    # --------------------------------------------------------
    # PLANNER → RESEARCH
    # --------------------------------------------------------

    graph.add_edge(
        "planner",
        "research"
    )

    # --------------------------------------------------------
    # RESEARCH → ANALYSIS
    # --------------------------------------------------------

    graph.add_edge(
        "research",
        "analysis"
    )

    # --------------------------------------------------------
    # ANALYSIS → PLANNER / VALIDATION
    # --------------------------------------------------------

    graph.add_conditional_edges(

        "analysis",

        research_decision,

        {

            "planner":
                "planner",

            "validation":
                "validation"
        }
    )

    # --------------------------------------------------------
    # VALIDATION → WRITER
    # --------------------------------------------------------

    graph.add_edge(
        "validation",
        "writer"
    )

    # --------------------------------------------------------
    # WRITER → END
    # --------------------------------------------------------

    graph.add_edge(
        "writer",
        END
    )

    return graph.compile()
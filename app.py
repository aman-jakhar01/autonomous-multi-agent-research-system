import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from workflow.orchestrator import build_workflow

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY", "")
tavily_api_key = os.getenv("TAVILY_API_KEY", "")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Autonomous Research AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "research_history" not in st.session_state:
    st.session_state["research_history"] = []

if "research_result" not in st.session_state:
    st.session_state["research_result"] = None


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.70;
        margin-bottom: 30px;
    }

    .section-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.20);
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔬 Autonomous Research AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Research complex topics using autonomous AI-powered
    web research, evidence analysis, validation, and report generation.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # RESEARCH SETTINGS
    # --------------------------------------------------------

    st.header("⚙️ Research Settings")

    max_rounds = st.slider(
        "Maximum Research Rounds",
        min_value=1,
        max_value=5,
        value=3,
        help=(
            "Maximum number of autonomous research "
            "rounds allowed."
        ),
    )

    st.divider()

    # --------------------------------------------------------
    # SYSTEM INFORMATION
    # --------------------------------------------------------

    st.header("ℹ️ About")

    st.markdown(
        """
        This application uses a multi-agent
        LangGraph workflow to:

        - Generate research queries
        - Search the web
        - Analyze evidence
        - Identify missing information
        - Perform additional research
        - Validate claims
        - Generate a final report
        """
    )

    st.divider()

    # --------------------------------------------------------
    # RESEARCH HISTORY
    # --------------------------------------------------------

    st.header("📚 Research History")

    history = st.session_state[
        "research_history"
    ]

    if not history:

        st.caption(
            "No research sessions yet."
        )

    else:

        st.caption(
            f"{len(history)} session(s)"
        )

        for item in reversed(history):

            with st.expander(
                item["topic"][:40]
            ):

                st.caption(
                    item["timestamp"]
                )

                st.write(
                    f"📚 Sources: "
                    f"{item['sources']}"
                )

                st.write(
                    f"📌 Claims: "
                    f"{item['claims']}"
                )

                st.write(
                    f"🎯 Confidence: "
                    f"{item['confidence']:.0%}"
                )

                st.write(
                    f"🔍 Validation: "
                    f"{item['validation']:.0%}"
                )


# ============================================================
# RESEARCH INPUT
# ============================================================

st.subheader("📝 Research Topic")

topic = st.text_area(
    "What would you like me to research?",
    placeholder=(
        "Examples:\n\n"
        "AI in healthcare in India\n\n"
        "Electric vehicle market in India\n\n"
        "Agricultural drone market in India\n\n"
        "Future of generative AI\n\n"
        "Battery swapping business in India"
    ),
    height=160,
)


# ============================================================
# RESEARCH BUTTON
# ============================================================

start_research = st.button(
    "🚀 Start Autonomous Research",
    type="primary",
    use_container_width=True,
)


# ============================================================
# RUN RESEARCH
# ============================================================

if start_research:

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not groq_api_key.strip():

        st.error(
            "❌ Built-in Groq API key is missing. Please set GROQ_API_KEY in .env."
        )

        st.stop()

    if not tavily_api_key.strip():

        st.error(
            "❌ Built-in Tavily API key is missing. Please set TAVILY_API_KEY in .env."
        )

        st.stop()

    if not topic.strip():

        st.error(
            "❌ Please enter a research topic."
        )

        st.stop()

    # --------------------------------------------------------
    # PROGRESS UI
    # --------------------------------------------------------

    st.markdown("---")

    st.subheader(
        "⚡ Research in Progress"
    )

    progress = st.progress(0)

    status = st.empty()

    status.info(
        "🚀 Initializing research..."
    )

    progress.progress(5)

    try:

        # ----------------------------------------------------
        # BUILD WORKFLOW
        # ----------------------------------------------------

        workflow = build_workflow()

        # ----------------------------------------------------
        # INITIAL STATE
        # ----------------------------------------------------

        initial_state = {

            "topic":
                topic.strip(),

            "research_queries":
                [],

            "sources":
                [],

            "analysis":
                "",

            "claims":
                [],

            "report":
                "",

            "needs_more_research":
                False,

            "missing_information":
                [],

            "confidence_score":
                0.0,

            "validation_score":
                0.0,

            "validation_issues":
                [],

            "research_round":
                0,

            "max_research_rounds":
                max_rounds,

            "groq_api_key":
                groq_api_key.strip(),

            "tavily_api_key":
                tavily_api_key.strip(),
        }

        # ----------------------------------------------------
        # STREAM LANGGRAPH
        # ----------------------------------------------------

        result = initial_state.copy()

        for event in workflow.stream(
            initial_state,
            stream_mode="updates",
        ):

            if not event:
                continue

            for node_name, node_update in event.items():

                # --------------------------------------------
                # MERGE STATE
                # --------------------------------------------

                if isinstance(
                    node_update,
                    dict
                ):

                    result.update(
                        node_update
                    )

                # --------------------------------------------
                # STATUS
                # --------------------------------------------

                if node_name == "planner":

                    status.info(
                        "🧠 Creating research queries..."
                    )

                    progress.progress(15)

                elif node_name == "research":

                    round_number = result.get(
                        "research_round",
                        1
                    )

                    status.info(
                        f"🔎 Searching the web "
                        f"(research round {round_number})..."
                    )

                    progress.progress(35)

                elif node_name == "analysis":

                    status.info(
                        "📊 Analyzing research "
                        "and identifying evidence..."
                    )

                    progress.progress(55)

                elif node_name == "validation":

                    status.info(
                        "🔍 Validating claims "
                        "and sources..."
                    )

                    progress.progress(75)

                elif node_name == "writer":

                    status.info(
                        "✍️ Generating final report..."
                    )

                    progress.progress(90)

        # ----------------------------------------------------
        # COMPLETED
        # ----------------------------------------------------

        progress.progress(100)

        status.success(
            "🎉 Research completed successfully!"
        )

        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        st.session_state[
            "research_result"
        ] = result

        # ----------------------------------------------------
        # SAVE HISTORY
        # ----------------------------------------------------

        st.session_state[
            "research_history"
        ].append(
            {
                "topic":
                    topic.strip(),

                "timestamp":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    ),

                "sources":
                    len(
                        result.get(
                            "sources",
                            []
                        )
                    ),

                "claims":
                    len(
                        result.get(
                            "claims",
                            []
                        )
                    ),

                "confidence":
                    result.get(
                        "confidence_score",
                        0.0
                    ),

                "validation":
                    result.get(
                        "validation_score",
                        0.0
                    ),
            }
        )

    except Exception as e:

        progress.progress(0)

        status.error(
            "❌ Research failed."
        )

        st.error(
            "An error occurred while running "
            "the research workflow."
        )

        with st.expander(
            "🔧 Technical Error"
        ):

            st.exception(e)


# ============================================================
# DISPLAY RESULTS
# ============================================================

result = st.session_state.get(
    "research_result"
)


if result:

    st.markdown("---")

    # ========================================================
    # RESEARCH OVERVIEW
    # ========================================================

    st.subheader(
        "📊 Research Overview"
    )

    sources = result.get(
        "sources",
        []
    )

    claims = result.get(
        "claims",
        []
    )

    confidence = result.get(
        "confidence_score",
        0.0
    )

    validation = result.get(
        "validation_score",
        0.0
    )

    research_round = result.get(
        "research_round",
        0
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "📚 Sources",
            len(sources)
        )

    with col2:

        st.metric(
            "📌 Claims",
            len(claims)
        )

    with col3:

        st.metric(
            "🎯 Confidence",
            f"{confidence:.0%}"
        )

    with col4:

        st.metric(
            "🔍 Validation",
            f"{validation:.0%}"
        )

    with col5:

        st.metric(
            "🔄 Research Rounds",
            research_round
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    st.markdown("---")

    st.subheader(
        "📄 Final Research Report"
    )

    report = result.get(
        "report",
        ""
    )

    if report:

        st.markdown(
            report
        )

        st.markdown(
            "### 📥 Download"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.download_button(
                label="📥 Download Markdown",
                data=report,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col2:

            st.download_button(
                label="📥 Download Text",
                data=report,
                file_name="research_report.txt",
                mime="text/plain",
                use_container_width=True,
            )

    else:

        st.warning(
            "No report was generated."
        )

    # ========================================================
    # VERIFIED CLAIMS
    # ========================================================

    st.markdown("---")

    st.subheader(
        "📌 Verified Claims"
    )

    if claims:

        for i, claim in enumerate(
            claims,
            start=1
        ):

            with st.expander(
                f"Claim {i}: {claim.claim}"
            ):

                if claim.evidence:

                    st.write(
                        "**Supporting Evidence**"
                    )

                    for evidence in (
                        claim.evidence
                    ):

                        st.info(
                            evidence.evidence
                        )

                        st.caption(
                            f"Source ID: "
                            f"{evidence.source_id}"
                        )

                else:

                    st.warning(
                        "No evidence attached."
                    )

    else:

        st.info(
            "No claims were extracted."
        )

    # ========================================================
    # VALIDATION ISSUES
    # ========================================================

    validation_issues = result.get(
        "validation_issues",
        []
    )

    if validation_issues:

        st.markdown("---")

        st.subheader(
            "⚠️ Validation Issues"
        )

        for issue in validation_issues:

            st.warning(
                issue
            )

    # ========================================================
    # SOURCES
    # ========================================================

    st.markdown("---")

    st.subheader(
        "🔗 Research Sources"
    )

    if sources:

        for i, source in enumerate(
            sources,
            start=1
        ):

            title = (
                source.title
                if source.title
                else "Untitled Source"
            )

            with st.expander(
                f"[{i}] {title}"
            ):

                col1, col2 = st.columns(
                    [3, 1]
                )

                with col1:

                    st.write(
                        f"**Domain:** "
                        f"{source.domain}"
                    )

                    st.write(
                        f"**Quality Score:** "
                        f"{source.quality_score:.0%}"
                    )

                    st.caption(
                        source.url
                    )

                with col2:

                    st.link_button(
                        "🌐 Open Source",
                        source.url,
                        use_container_width=True,
                    )

                if source.content:

                    st.write(
                        source.content[:1000]
                    )

    else:

        st.warning(
            "No sources were returned."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🔬 Autonomous Research AI • "
    "LangGraph Multi-Agent Research System"
)
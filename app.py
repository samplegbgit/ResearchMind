import streamlit as st
from groq import RateLimitError, APIConnectionError, APIStatusError
from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain,
)



st.set_page_config(
    page_title="ResearchMind | AI Research Assistant",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)



st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');

    :root {
        --bg: #0b0b10;
        --panel: #12121a;
        --panel2: #171720;
        --border: #292936;
        --orange: #ff8c32;
        --text: #f3f3f7;
        --muted: #a0a0b2;
        --green: #58d68d;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* HERO */

    .hero {
        text-align: center;
        padding: 35px 10px 30px;
    }

    .hero-tag {
        color: var(--orange);
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(42px, 7vw, 72px);
        font-weight: 800;
        letter-spacing: -3px;
        line-height: 1.05;
        margin: 0;
        color: var(--text);
    }

    .hero-title span {
        color: var(--orange);
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 16px;
        margin-top: 17px;
    }

    .section-label {
        color: var(--orange);
        font-family: 'DM Mono', monospace;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    /* PANELS */

    .panel {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 15px;
        padding: 22px;
        margin: 12px 0;
    }

    .panel-title {
        font-family: 'Syne', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 8px;
    }

    .muted {
        color: var(--muted);
        font-size: 14px;
    }

    /* RESEARCH TOPIC INPUT: DARK BACKGROUND */

    div[data-testid="stTextInput"] {
        color: #f5f5f5 !important;
    }

    div[data-testid="stTextInput"] [data-baseweb="base-input"],
    div[data-testid="stTextInput"] [data-baseweb="input"] {
        background-color: #15151d !important;
        border: 1px solid #ff8c32 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] input {
        background: #15151d !important;
        background-color: #15151d !important;
        color: #f5f5f5 !important;
        -webkit-text-fill-color: #f5f5f5 !important;
        caret-color: #ff8c32 !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 52px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 17px !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #a0a0ad !important;
        -webkit-text-fill-color: #a0a0ad !important;
        opacity: 1 !important;
    }

    div[data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within,
    div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
        border: 1px solid #ff8c32 !important;
        box-shadow: 0 0 0 1px #ff8c32 !important;
    }

    /* BUTTONS: KEEP ORANGE */

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        background: #ff8c32 !important;
        color: #151515 !important;
        border: none !important;
        border-radius: 9px !important;
        padding: 10px 22px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #ffab66 !important;
        color: #151515 !important;
        transform: translateY(-1px);
    }

    .stButton > button:disabled,
    .stFormSubmitButton > button:disabled {
        background: #55515a !important;
        color: #c8c5cc !important;
    }

    /* PIPELINE CARDS */

    .step-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        min-height: 125px;
        margin-bottom: 8px;
    }

    .step-number {
        color: var(--orange);
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        letter-spacing: 2px;
    }

    .step-name {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 16px;
        margin-top: 9px;
        color: var(--text);
    }

    .step-description {
        color: var(--muted);
        font-size: 12px;
        margin-top: 5px;
    }

    /* EXPANDERS AND STATUS */

    [data-testid="stExpander"] {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    [data-testid="stStatusWidget"] {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {
        color: var(--text);
    }

    /* DIVIDERS AND FOOTER */

    hr {
        border-color: var(--border) !important;
    }

    .footer {
        text-align: center;
        color: #777787;
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 1px;
        padding-top: 30px;
    }

    label, .stCaption {
        color: var(--muted) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)




def extract_agent_text(response):
    """Extract readable text from a LangChain agent response."""

    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        messages = response.get("messages", [])

        for message in reversed(messages):
            content = getattr(message, "content", None)

            if isinstance(content, str) and content.strip():
                return content

            if isinstance(content, list):
                parts = []

                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))
                    elif isinstance(item, str):
                        parts.append(item)

                if parts:
                    return "\n".join(parts)

        return str(response)

    return str(response)


def step_card(number, name, description):
    st.markdown(
        f"""
        <div class="step-card">
            <div class="step-number">STEP {number}</div>
            <div class="step-name">{name}</div>
            <div class="step-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )




if "results" not in st.session_state:
    st.session_state.results = {
        "search_results": "",
        "scraped_content": "",
        "report": "",
        "feedback": "",
    }

if "done" not in st.session_state:
    st.session_state.done = False

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

if "failed_stage" not in st.session_state:
    st.session_state.failed_stage = ""

if "running" not in st.session_state:
    st.session_state.running = False


-

st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">Your AI-Powered Research Workspace</div>
        <h1 class="hero-title">Research<span>Mind</span></h1>
        <div class="hero-subtitle">
            From web research to a structured report, powered by AI agents.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)




st.markdown(
    '<div class="section-label">THE RESEARCH PIPELINE</div>',
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    step_card("01", "Search Agent", "Find relevant web sources")

with col2:
    step_card("02", "Reader Agent", "Read and extract useful information")

with col3:
    step_card("03", "Research Writer", "Generate a structured report")

with col4:
    step_card("04", "Critic Agent", "Review and score the report")




st.markdown("---")

st.markdown(
    '<div class="section-label">RESEARCH TOPIC</div>',
    unsafe_allow_html=True,
)

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Benefits of reading books",
        label_visibility="collapsed",
        disabled=st.session_state.running,
    )

    submitted = st.form_submit_button(
        "Start Research →",
        use_container_width=True,
        disabled=st.session_state.running,
    )

if submitted:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        st.session_state.last_topic = topic.strip()
        st.session_state.results = {
            "search_results": "",
            "scraped_content": "",
            "report": "",
            "feedback": "",
        }
        st.session_state.done = False
        st.session_state.error_message = ""
        st.session_state.failed_stage = ""
        st.session_state.running = True
        st.rerun()



if st.session_state.running:
    topic = st.session_state.last_topic
    results = st.session_state.results

    st.markdown("---")
    st.markdown(
        '<div class="section-label">LIVE PIPELINE EXECUTION</div>',
        unsafe_allow_html=True,
    )

    try:
        
        if not results["search_results"]:
            with st.status(
                "Step 1/4 — Searching the web...",
                expanded=True,
            ) as status:
                st.write("Finding relevant sources for your topic.")

                search_agent = build_search_agent()

                search_prompt = f"""
                Research the following topic: {topic}

                Use the web_search tool with a text query.
                The tool accepts a query string, not a URL.
                Return the results with titles, URLs, and snippets.
                Do not invent URLs or unsupported facts.
                """

                search_response = search_agent.invoke(
                    {
                        "messages": [("user", search_prompt)]
                    }
                )

                results["search_results"] = extract_agent_text(
                    search_response
                )
                st.session_state.results = dict(results)

                status.update(
                    label="Step 1/4 — Web search completed",
                    state="complete",
                    expanded=False,
                )

        
        if not results["scraped_content"]:
            with st.status(
                "Step 2/4 — Reading sources...",
                expanded=True,
            ) as status:
                st.write("Extracting readable content from a relevant URL.")

                reader_agent = build_reader_agent()

                reader_prompt = f"""
                Topic: {topic}

                Search results:
                {results["search_results"][:6000]}

                Select a relevant URL from the search results and call
                scrape_url with that URL. Do not call web_search with a URL.
                Summarize only content actually returned by the tool.
                Clearly mention if scraping fails. Do not invent statistics.
                """

                reader_response = reader_agent.invoke(
                    {
                        "messages": [("user", reader_prompt)]
                    }
                )

                results["scraped_content"] = extract_agent_text(
                    reader_response
                )
                st.session_state.results = dict(results)

                status.update(
                    label="Step 2/4 — Source reading completed",
                    state="complete",
                    expanded=False,
                )

        
        if not results["report"]:
            with st.status(
                "Step 3/4 — Writing the research report...",
                expanded=True,
            ) as status:
                st.write("Generating a structured research report.")

                research_combined = (
                    "WEB SEARCH RESULTS:\n"
                    + results["search_results"]
                    + "\n\nSCRAPED SOURCE CONTENT:\n"
                    + results["scraped_content"]
                )

                report = writer_chain.invoke(
                    {
                        "topic": topic,
                        "research": research_combined,
                    }
                )

                results["report"] = report
                st.session_state.results = dict(results)

                status.update(
                    label="Step 3/4 — Report generated",
                    state="complete",
                    expanded=False,
                )

       
        if not results["feedback"]:
            with st.status(
                "Step 4/4 — Reviewing the report...",
                expanded=True,
            ) as status:
                st.write("Evaluating report quality and completeness.")

                feedback = critic_chain.invoke(
                    {"report": results["report"]}
                )

                results["feedback"] = feedback
                st.session_state.results = dict(results)

                status.update(
                    label="Step 4/4 — Review completed",
                    state="complete",
                    expanded=False,
                )

        st.session_state.running = False
        st.session_state.done = True
        st.session_state.error_message = ""
        st.session_state.failed_stage = ""
        st.rerun()

    except RateLimitError as e:
        st.session_state.running = False
        st.session_state.error_message = str(e)
        st.session_state.failed_stage = "Rate limit"

    except APIConnectionError as e:
        st.session_state.running = False
        st.session_state.error_message = str(e)
        st.session_state.failed_stage = "Connection"

    except APIStatusError as e:
        st.session_state.running = False
        st.session_state.error_message = str(e)
        st.session_state.failed_stage = "API request"

    except Exception as e:
        st.session_state.running = False
        st.session_state.error_message = (
            f"{type(e).__name__}: {str(e)}"
        )
        st.session_state.failed_stage = "Pipeline"




if st.session_state.error_message:
    st.markdown("---")

    st.error(
        f"**{st.session_state.failed_stage} error**\n\n"
        f"{st.session_state.error_message}"
    )

    st.info(
        "Completed stages have been preserved where possible. "
        "Click Retry to continue from the last saved stage."
    )

    if st.button("Retry Research", use_container_width=True):
        st.session_state.error_message = ""
        st.session_state.failed_stage = ""
        st.session_state.running = True
        st.rerun()




if st.session_state.done:
    results = st.session_state.results

    st.markdown("---")
    st.markdown(
        '<div class="section-label">RESEARCH RESULTS</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="panel">
            <div class="muted">RESEARCH TOPIC</div>
            <div class="panel-title">
                {st.session_state.last_topic}
            </div>
            <div class="muted">
                All four pipeline stages have finished.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("01 — Web Search Results"):
        st.markdown(
            results["search_results"] or "No search results available."
        )

    with st.expander("02 — Scraped Source Content"):
        st.markdown(
            results["scraped_content"] or "No scraped content available."
        )

    st.markdown(
        '<div class="section-label">GENERATED REPORT</div>',
        unsafe_allow_html=True,
    )

    st.markdown(results["report"] or "No report generated.")

    if results["report"]:
        st.download_button(
            label="Download Research Report (.md)",
            data=results["report"],
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown(
        '<div class="section-label">CRITIC REVIEW</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Report Evaluation</div>
            <div class="muted">
                Feedback generated by the Critic Agent
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(results["feedback"] or "No critic feedback available.")

    st.markdown("---")

    if st.button("Start New Research", use_container_width=True):
        st.session_state.results = {
            "search_results": "",
            "scraped_content": "",
            "report": "",
            "feedback": "",
        }
        st.session_state.done = False
        st.session_state.last_topic = ""
        st.session_state.error_message = ""
        st.session_state.failed_stage = ""
        st.session_state.running = False
        st.rerun()




st.markdown(
    """
    <div class="footer">
        RESEARCHMIND · AI-POWERED RESEARCH WORKSPACE
    </div>
    """,
    unsafe_allow_html=True,
)

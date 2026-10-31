
from pathlib import Path
from html import escape

import streamlit as st

from ripple.engine import run_ripple


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Ripple | Developer Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.stApp {
    background: #080f1e;
    color: #e5edf8;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #101a2c;
    border-right: 1px solid #263650;
}

.hero {
    background: linear-gradient(120deg, #10243e, #111b31);
    border: 1px solid #254363;
    border-radius: 18px;
    padding: 30px;
    margin-bottom: 24px;
}

.hero-title {
    color: #38bdf8;
    font-size: 42px;
    font-weight: 850;
    letter-spacing: 2px;
    margin: 0;
}

.hero-subtitle {
    color: #b5c5da;
    font-size: 16px;
    margin-top: 8px;
}

.hero-tag {
    display: inline-block;
    color: #7dd3fc;
    background: #123452;
    border: 1px solid #245778;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    margin-top: 15px;
}

div[data-testid="stMetric"] {
    background: #142137;
    border: 1px solid #263d5b;
    border-radius: 14px;
    padding: 20px;
}

div[data-testid="stMetricLabel"] {
    color: #a9bbd2;
}

div[data-testid="stMetricValue"] {
    color: #f1f7ff;
    font-weight: 750;
}

.section-label {
    color: #38bdf8;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 2px;
    margin-bottom: 5px;
}

.impact-card {
    background: #142137;
    border: 1px solid #29415f;
    border-radius: 13px;
    padding: 18px;
    margin-bottom: 12px;
}

.impact-source {
    color: #fbbf24;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.impact-target {
    color: #7dd3fc;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.impact-arrow {
    color: #38bdf8;
    font-size: 20px;
    font-weight: 800;
    margin: 10px 0;
}

.status-pill {
    display: inline-block;
    background: #123d35;
    color: #6ee7b7;
    border: 1px solid #17634e;
    border-radius: 20px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
}

.stButton button[kind="primary"] {
    background: linear-gradient(90deg, #0284c7, #2563eb);
    border: none;
    border-radius: 9px;
    padding: 10px 22px;
    font-weight: 700;
}

.stButton button[kind="primary"]:hover {
    background: linear-gradient(90deg, #0369a1, #1d4ed8);
    border: none;
}

hr {
    border-color: #263650;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def safe_text(value):
    """Escape dynamic text before rendering HTML."""
    return escape(str(value))


def display_module_relationship(source, target):
    """Display a dependency relationship."""

    source = safe_text(source)
    target = safe_text(target)

    st.html(f"""
<div class="impact-card">
    <div style="color:#94a3b8;font-size:12px;letter-spacing:1px;">
        DEPENDENCY RELATIONSHIP
    </div>
    <div class="impact-source">
        🟠 {source}
    </div>
    <div class="impact-arrow">
        ↓ Affects
    </div>
    <div class="impact-target">
        🔵 {target}
    </div>
</div>
""")


def section_heading(label, heading):
    st.markdown(
        f'<div class="section-label">{safe_text(label)}</div>',
        unsafe_allow_html=True,
    )
    st.header(heading)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown("## 🌊 Ripple")
    st.caption("Developer Intelligence Platform")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Impact Analysis",
            "Test Recommendations",
        ],
    )
    st.markdown("### Target Repository")

    target_repo_path = st.text_input(
        "Repository path",
        value=str(ROOT),
        help="Enter the absolute path to a Git repository.",
    )
    st.divider()

    st.markdown("### Supported Languages")
    st.markdown("🐍 Python")
    st.markdown("🟨 JavaScript")

    st.divider()

    st.caption("Powered by Ripple Intelligence Engine")
    st.caption("Change Impact • Dependency Analysis • Testing")


# ==================================================
# HERO SECTION
# ==================================================

st.html("""
<div class="hero">
    <p class="hero-title">🌊 RIPPLE</p>
    <p class="hero-subtitle">
        Change Impact Intelligence Platform
    </p>
    <span class="hero-tag">
        DEVELOPER INTELLIGENCE
    </span>
</div>
""")


# ==================================================
# ANALYSIS CONTROL
# ==================================================

control_col, status_col = st.columns([1, 3])

with control_col:

    run_clicked = st.button(
        "🚀 Run Ripple Analysis",
        type="primary",
        use_container_width=True,
    )

if run_clicked:

    with st.spinner(
        "Analyzing dependencies and executing recommended tests..."
    ):

        try:
            target_root = Path(target_repo_path).expanduser().resolve()

            if not target_root.is_dir():
                st.error("Invalid repository path. Please enter a valid directory.")
                st.stop()

            results = run_ripple(target_root)

            if results is None:
                st.warning(
                    "The engine returned no results. "
                    "Check whether repository changes are detectable."
                )

            else:
                st.session_state["ripple_results"] = results
                st.session_state["analysis_error"] = None

        except Exception as error:
         st.session_state["analysis_error"] = str(error)

if st.session_state.get("analysis_error"):

    st.error(
        f"Analysis failed: {st.session_state['analysis_error']}"
    )

results = st.session_state.get("ripple_results")

if results is not None:

    with status_col:
        st.markdown(
            '<span class="status-pill">● ANALYSIS RESULTS AVAILABLE</span>',
            unsafe_allow_html=True,
        )


# ==================================================
# NO RESULTS STATE
# ==================================================

if results is None:

    st.info(
        "Run Ripple Analysis to inspect repository changes, "
        "trace dependencies and recommend relevant tests."
    )

    st.markdown("### How Ripple Works")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 01 · Detect")
        st.write("Identify modified source files through Git.")

    with col2:
        st.markdown("#### 02 · Analyze")
        st.write("Trace dependencies and identify potentially impacted modules.")

    with col3:
        st.markdown("#### 03 · Validate")
        st.write("Recommend and execute relevant automated tests.")


# ==================================================
# RESULTS
# ==================================================

else:

    summary = results["summary"]


    # ==================================================
    # OVERVIEW
    # ==================================================

    if page == "Overview":

        section_heading(
            "PROJECT DASHBOARD",
            "Project Overview",
        )

        st.caption(
            "A snapshot of detected changes, dependency impact and testing."
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Changed Modules",
            summary["changed_modules"],
        )

        col2.metric(
            "Impacted Modules",
            summary["impacted_modules"],
        )

        col3.metric(
            "Tests Recommended",
            summary["tests_recommended"],
        )

        col4.metric(
            "Dependency Relationships",
            summary["dependency_relationships"],
        )

        st.divider()

        st.subheader("Analysis Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Files Analyzed",
            summary["analyzed_files"],
        )

        col2.metric(
            "Tests Discovered",
            summary["tests_discovered"],
        )

        col3.metric(
            "Tests Passed",
            summary["tests_passed"],
        )

        st.metric(
            "Tests Failed",
            summary["tests_failed"],
        )

        st.divider()

        if summary["tests_recommended"] == 0:

            st.warning(
                "No tests were recommended. "
                "No tests were executed."
            )

        elif (
            summary["tests_passed"] + summary["tests_failed"] == 0
        ):

            st.warning(
                "Recommended tests were not executed."
            )

        elif summary["execution_successful"]:

            st.success(
                "All executed recommended tests passed."
            )

        else:

            st.error(
                "Test execution reported a failure."
            )


    # ==================================================
    # IMPACT ANALYSIS
    # ==================================================

    elif page == "Impact Analysis":

        section_heading(
            "DEPENDENCY INTELLIGENCE",
            "Change Impact Analysis",
        )

        changed_modules = results["changed_modules"]
        impacted = results["impacted_modules"]

        st.subheader("Changed Modules")

        if changed_modules:

            for module in changed_modules:
                st.markdown(f"🟠 `{module}`")

        else:

            st.info("No changed source modules detected.")

        st.divider()

        st.subheader("Impact Statistics")

        direct_count = sum(
            1
            for details in impacted.values()
            if details["impact_type"] == "direct"
        )

        indirect_count = sum(
            1
            for details in impacted.values()
            if details["impact_type"] == "indirect"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Impacted", len(impacted))
        col2.metric("Direct Impact", direct_count)
        col3.metric("Indirect Impact", indirect_count)

        st.divider()

        st.subheader("Dependency Impact Flow")

        st.caption(
            "Follow the dependency relationships to understand "
            "how changes can affect downstream modules."
        )

        if impacted:

            for module, details in impacted.items():

                source = details.get(
                    "affected_by",
                    "Unknown source",
                )

                display_module_relationship(
                    source,
                    module,
                )

        else:

            st.info(
                "No additional impacted modules detected."
            )

        st.divider()

        st.subheader("Detailed Impact Breakdown")

        if impacted:

            for module, details in impacted.items():

                impact_type = details["impact_type"]
                depth = details["depth"]

                with st.expander(
                    f"{module} — {impact_type.upper()}"
                ):

                    col1, col2 = st.columns(2)

                    col1.metric("Impact Depth", depth)

                    col2.metric(
                        "Impact Type",
                        impact_type.capitalize(),
                    )

                    st.write(
                        "**Affected by:**",
                        details.get(
                            "affected_by",
                            "Not available",
                        ),
                    )

                    if depth == 1:
                        st.success("Direct dependency impact.")

                    else:
                        st.warning(
                            f"Indirect impact at dependency level {depth}."
                        )

        else:

            st.info("No detailed impact information is available.")

        st.divider()

        st.subheader("Changed Files")

        for change in results["changed_files"]:

            st.write(
                f"**{change['change_type'].upper()}** — "
                f"`{change['file']}`"
            )


    # ==================================================
    # TEST RECOMMENDATIONS
    # ==================================================

    elif page == "Test Recommendations":

        section_heading(
            "AUTOMATED VALIDATION",
            "Test Recommendations",
        )

        recommendations = results["recommendations"]

        col1, col2 = st.columns(2)

        col1.metric(
            "Tests Discovered",
            summary["tests_discovered"],
        )

        col2.metric(
            "Tests Recommended",
            summary["tests_recommended"],
        )

        st.divider()

        st.subheader("Recommended Test Cases")

        if recommendations:

            for item in recommendations:

                with st.expander(item["test_file"]):

                    col1, col2 = st.columns(2)

                    priority = item.get("priority", "medium").upper()
                    match_type = item.get("match_type", "unknown")

                    col1.metric("Priority", priority)

                    col2.metric(
                        "Matching Method",
                        match_type.replace("_", " ").title(),
                    )

                    st.write("**Matched Modules**")

                    for module in item["matched_modules"]:
                        st.write(f"- `{module}`")

                    st.write("**Why Ripple Recommended This Test**")
                    st.info(item["reason"])

            if results["test_results"]["success"]:
                st.success("Automated test execution completed successfully.")
            else:
                st.error("Automated test execution reported failures.")

        else:

            st.warning(
                "No matching tests were recommended."
            )
    else:

        st.warning(
                "No matching tests were recommended."
            )

        st.divider()

        st.subheader("Test Execution Results")

        test_results = results["test_results"]

        col1, col2 = st.columns(2)

        col1.metric(
            "Passed",
            test_results["passed"],
        )

        col2.metric(
            "Failed",
            test_results["failed"],
        )

        if test_results["success"]:

            st.success("Test execution completed successfully.")

        else:

            st.error("Test execution was not fully successful.")

        if test_results["output"]:

            with st.expander("View Detailed Test Output"):

                st.code(
                    test_results["output"],
                    language="text",
                )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "🌊 Ripple | Change Impact Intelligence | "
    "Python + JavaScript"
)

"""Home page for the Pilk-DCE WebUI"""

import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

from pilk_dce.webui.utils import get_example_config, create_sample_dataset, create_efficiency_trace


def render_home():
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 1rem;">
        <div>
            <h1 style="margin: 0;">Pilk-DCE Dashboard</h1>
            <p style="color: rgba(226, 232, 240, 0.8);">
                A polished control center for discrete choice experiment design, analysis, and
                insightful visualization.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Highlights
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Current Study", value="Coffee Preference", delta="v0.1.0")
    col2.metric(label="Design Readiness", value="78%", delta="+12% from baseline")
    col3.metric(label="Analytical Confidence", value="95%", delta="+3% vs last run")

    st.markdown("---")

    with st.container():
        st.markdown("""
        <div class="metric-card fade-in">
            <h3>Quick Launch</h3>
            <ol style="color: #CBD5F5;">
                <li>Upload or create your YAML config in the Generator tab.</li>
                <li>Run optimization and tune sample sizes with the Analyzer.</li>
                <li>Visualize part-worths, WTP, and market share without leaving the browser.</li>
            </ol>
            <p style="color: #94A3B8; margin-top: 0.5rem;">Need inspiration? Load the example config below.</p>
        </div>
        """, unsafe_allow_html=True)

        # Example config showcase
        example = get_example_config()
        st.code(example, language="yaml")

    st.markdown("---")

    # Efficiency trace
    trace = create_efficiency_trace(45, 68, iterations=120)
    trace_df = pd.DataFrame({"Iteration": range(len(trace)), "Efficiency": trace})
    chart = alt.Chart(trace_df).mark_line(point=True).encode(
        x=alt.X("Iteration", axis=alt.Axis(labelColor="#94A3B8")),
        y=alt.Y("Efficiency", axis=alt.Axis(labelColor="#94A3B8")),
        tooltip=[alt.Tooltip("Iteration"), alt.Tooltip("Efficiency", format=".2f")]
    ).properties(height=260)
    st.altair_chart(chart, use_container_width=True)
    st.caption("Optimization trace with synthetic convergence and noise")

    st.markdown("---")

    # Sample dataset preview
    sample = create_sample_dataset(120)
    respondents = sample['respondent_id'].nunique()
    choices = sample['choice'].mean() * 100
    share = sample.groupby('alternative')['choice'].mean().reset_index()

    st.subheader("Snapshot: Sample Responses")
    st.markdown(
        f"Respondents surveyed: **{respondents}** | Choice share: **{choices:.1f}%**",
        unsafe_allow_html=True
    )
    st.dataframe(sample.head(6), column_config={
        "respondent_id": "Respondent ID",
        "choice_set": "Choice Set",
        "alternative": "Alternative",
        "choice": "Chosen",
    }, hide_index=True)

    share_chart = alt.Chart(share).mark_bar().encode(
        x=alt.X("alternative:O", title="Alternative", sort="-y", axis=alt.Axis(labelColor="#94A3B8")),
        y=alt.Y("choice", title="Empirical preference", axis=alt.Axis(labelColor="#94A3B8")),
        color=alt.Color("alternative:O", legend=None),
        tooltip=[alt.Tooltip("alternative"), alt.Tooltip("choice", format=".2f")]
    ).properties(height=220)
    st.altair_chart(share_chart, use_container_width=True)

    st.markdown("---")

    st.caption("Use the sidebar to jump between Generator, Analyzer, Visualizer, Designer, and Export pages.")

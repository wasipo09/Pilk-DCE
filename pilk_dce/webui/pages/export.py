"""Export page for the Pilk-DCE WebUI"""

import streamlit as st
from pilk_dce.webui.utils import (
    create_download_csv,
    create_download_json,
    create_download_zip,
    create_sample_dataset
)


def render_export():
    st.markdown("""
    <div>
        <h2>Export Dashboard</h2>
        <p style="color: rgba(226, 232, 240, 0.8);">
            Download configurations, design matrices, and analytics packages in CSV, JSON, or ZIP formats.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.design_data is None:
        st.warning("Generate a design before you can export results.")
        st.stop()

    design_df = st.session_state.design_data
    metrics = st.session_state.optimization_results.get('metrics', {}) if st.session_state.optimization_results else {}

    csv_name, csv_data = create_download_csv(design_df, filename='design_matrix.csv')
    json_name, json_data = create_download_json(metrics, filename='metrics.json')
    package_name, package_data = create_download_zip([
        (csv_name, csv_data),
        (json_name, json_data)
    ])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=csv_name,
            mime='text/csv'
        )
    with col2:
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=json_name,
            mime='application/json'
        )
    with col3:
        st.download_button(
            label="Download ZIP Package",
            data=package_data,
            file_name=package_name,
            mime='application/zip'
        )

    st.markdown("---")
    st.subheader("Shareable Package Contents")
    st.write("• design_matrix.csv — choice tasks with encoded levels")
    st.write("• metrics.json — optimization summary metrics")

    sample = create_sample_dataset(60)
    sample_csv, sample_data = create_download_csv(sample, filename='sample_responses.csv')
    st.markdown("---")
    st.download_button(
        "Download sample dataset",
        data=sample_data,
        file_name=sample_csv,
        mime='text/csv'
    )

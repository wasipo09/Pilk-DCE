"""Generator page for the Pilk-DCE WebUI"""

import streamlit as st
import time
import json

from pilk_dce.webui.utils import (
    load_yaml_config,
    validate_config,
    create_dce_model,
    generate_design,
    create_download_csv,
    create_download_zip,
    get_example_config
)


def render_generator():
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2>Config Generator &amp; Synthetic Data</h2>
            <p style="color: rgba(226, 232, 240, 0.8);">
                Upload YAML specs, tune optimization strategies, and export instant design matrices.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Session defaults
    if 'generator_config_text' not in st.session_state:
        st.session_state.generator_config_text = get_example_config()

    uploaded_file = st.file_uploader(
        "Drag & drop your YAML config",
        type=['yaml', 'yml'],
        accept_multiple_files=False,
        help="Use example configs from the Examples folder if you're experimenting."
    )

    if uploaded_file:
        st.session_state.uploaded_files['config'] = uploaded_file.name
        if st.button("Load uploaded config into editor"):
            st.session_state.generator_config_text = uploaded_file.getvalue().decode('utf-8')
            st.success("Configuration loaded into the editor")

    with st.expander("Live YAML Editor", expanded=True):
        st.session_state.generator_config_text = st.text_area(
            "Configuration",
            value=st.session_state.generator_config_text,
            height=340,
            placeholder="Paste a DCE config here or load an example",
            help="The editor supports drag-and-drop, validation, and instant preview."
        )
        try:
            config = load_yaml_config(st.session_state.generator_config_text)
            is_valid, errors = validate_config(config)
            if is_valid:
                st.success("Configuration is valid")
            else:
                st.error("Configuration issues detected")
                for msg in errors:
                    st.write(f"• {msg}")
        except ValueError as exc:
            st.error(f"Unable to parse YAML: {exc}")
            config = None

    st.markdown("---")

    st.subheader("Optimization Strategy")
    optimization_type = st.selectbox(
        "Choose optimization type",
        ['d-optimal', 'g-optimal', 'i-optimal', 'bayesian', 'sample-size']
    )

    bayesian_params = {}
    sample_size_target = None

    if optimization_type == 'bayesian':
        with st.expander("Bayesian Prior Explorer"):
            dist = st.selectbox("Prior distribution", ['normal', 'beta', 'uniform'])
            if dist == 'normal':
                mu = st.number_input("Mean", value=-0.05, step=0.01)
                sd = st.number_input("Standard deviation", value=0.02, step=0.01, min_value=0.001)
                bayesian_params = {'prior_distribution': 'normal', 'prior_params': {'mean': mu, 'sd': sd}}
            elif dist == 'beta':
                a = st.number_input("Alpha", value=2.0)
                b = st.number_input("Beta", value=2.0)
                bayesian_params = {'prior_distribution': 'beta', 'prior_params': {'alpha': a, 'beta': b}}
            else:
                bayesian_params = {'prior_distribution': 'uniform', 'prior_params': {}}
    elif optimization_type == 'sample-size':
        sample_size_target = st.slider("Target sample size", min_value=50, max_value=500, value=200, step=10)

    generate_col1, generate_col2 = st.columns([3, 1])
    with generate_col1:
        generate = st.button("Generate design", type='primary')
    with generate_col2:
        st.download_button(
            "Download example config",
            data=get_example_config().encode('utf-8'),
            file_name='example-config.yaml',
            mime='text/yaml'
        )

    if generate:
        if not config:
            st.error("Please fix the configuration before generating a design.")
        else:
            model = create_dce_model(config)
            progress_bar = st.progress(0)
            try:
                with st.spinner("Crafting optimized design..."):
                    for pct in range(0, 101, 25):
                        time.sleep(0.1)
                        progress_bar.progress(pct / 100)
                    kwargs = {}
                    if optimization_type == 'bayesian':
                        kwargs = bayesian_params
                    if optimization_type == 'sample-size':
                        kwargs = {'target_size': sample_size_target}
                    results = generate_design(model, optimization_type=optimization_type, **kwargs)
                    st.session_state.design_data = results['optimized_design']
                    st.session_state.optimization_results = results
                    st.success("Design generated successfully")
            except Exception as exc:
                st.error(f"Optimization failed: {str(exc)}")
            finally:
                progress_bar.progress(1)

    if st.session_state.optimization_results:
        results = st.session_state.optimization_results
        metrics = results.get('metrics', {})
        st.markdown("---")
        st.subheader("Optimization Summary")
        metric_cols = st.columns(4)
        metric_cols[0].metric("Design Type", results.get('design_type', 'Unknown'))
        metric_cols[1].metric("Success", "Yes" if metrics.get('Success') else "Pending")
        metric_cols[2].metric("Iterations", metrics.get('Iterations', 0))
        metric_cols[3].metric("D-efficiency", f"{metrics.get('D-efficiency', 0):.2f}")

        st.markdown("---")
        st.subheader("Design Preview")
        st.dataframe(results['optimized_design'].head(10))

        filename, data = create_download_csv(results['optimized_design'], filename='design_matrix.csv')
        st.download_button("Download design CSV", data=data, file_name=filename, mime='text/csv')

        package_files = [
            ("design_matrix.csv", data),
            ("metrics.json", json.dumps(metrics, indent=2).encode('utf-8'))
        ]
        _, zip_data = create_download_zip(package_files)
        st.download_button("Download full package", data=zip_data, file_name='design_package.zip', mime='application/zip')

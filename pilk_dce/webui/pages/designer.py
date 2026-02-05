"""Designer page for the Pilk-DCE WebUI"""

import streamlit as st
import yaml
from pilk_dce.webui.utils import get_example_config, create_dce_model
from pilk_dce.webui.visualizations import bayesian_prior_chart


def render_designer():
    st.markdown("""
    <div>
        <h2>Attribute Designer</h2>
        <p style="color: rgba(226, 232, 240, 0.8);">
            Create attributes, tune alternatives, and preview the YAML configuration in real time.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if 'designer_attributes' not in st.session_state:
        st.session_state.designer_attributes = []
    if 'designer_alternatives' not in st.session_state:
        st.session_state.designer_alternatives = 3
    if 'designer_choice_sets' not in st.session_state:
        st.session_state.designer_choice_sets = 12

    with st.expander("Add new attribute", expanded=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Attribute name", key='designer_attr_name')
        levels = col2.text_input("Levels (comma separated)", key='designer_attr_levels')
        description = st.text_input("Description", placeholder="Optional attribute description")
        if st.button("Add attribute"):
            if name and levels:
                level_list = [val.strip() for val in levels.split(',') if val.strip()]
                st.session_state.designer_attributes.append({
                    'name': name,
                    'levels': level_list,
                    'description': description
                })
                st.success(f"Added attribute {name}")
            else:
                st.warning("Attribute name and levels are required.")

    if st.session_state.designer_attributes:
        st.markdown("**Current attributes**")
        for attr in st.session_state.designer_attributes:
            st.markdown(f"- **{attr['name']}**: {', '.join(attr['levels'])}")
    else:
        st.info("Add attributes to build the configuration.")

    st.markdown("---")

    cols = st.columns(2)
    st.session_state.designer_alternatives = cols[0].slider("Alternatives per choice set", 2, 6, st.session_state.designer_alternatives)
    st.session_state.designer_choice_sets = cols[1].slider("Choice sets", 4, 20, st.session_state.designer_choice_sets)

    if st.button("Reset attributes", use_container_width=True):
        st.session_state.designer_attributes = []
        st.success("Attributes cleared")

    config = {
        'attributes': st.session_state.designer_attributes,
        'alternatives': st.session_state.designer_alternatives,
        'choice_sets': st.session_state.designer_choice_sets
    }

    preview_yaml = yaml.dump(config, sort_keys=False)
    st.markdown("**Live YAML preview**")
    st.code(preview_yaml, language='yaml')

    if st.button("Generate preview design matrix"):
        try:
            model = create_dce_model(config)
            design = model.generate_design()
            st.session_state.design_data = design
            st.dataframe(design.head(10))
        except Exception as exc:
            st.error(f"Preview failed: {exc}")

    st.markdown("---")
    st.subheader("Bayesian prior visualizer")
    dist = st.selectbox("Prior type", ['normal', 'beta', 'uniform'])
    params = {}
    if dist == 'normal':
        params['mean'] = st.slider("Mean", -0.2, 0.2, 0.0, step=0.01)
        params['sd'] = st.slider("Standard deviation", 0.01, 0.5, 0.1, step=0.01)
    elif dist == 'beta':
        params['alpha'] = st.slider("Alpha", 0.5, 5.0, 2.0, step=0.1)
        params['beta'] = st.slider("Beta", 0.5, 5.0, 2.0, step=0.1)
    chart = bayesian_prior_chart(dist, params)
    if chart:
        st.altair_chart(chart, use_container_width=True)

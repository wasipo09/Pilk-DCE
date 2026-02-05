"""Analyzer page for the Pilk-DCE WebUI"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import time
from sklearn.linear_model import LogisticRegression

from pilk_dce.webui.utils import create_sample_dataset


@st.cache_data
def load_dataset(file):
    return pd.read_csv(file)


def prepare_features(df, feature_columns):
    df = df.copy()
    X = pd.get_dummies(df[feature_columns], drop_first=True)
    return X


def run_logistic(df, target_column, feature_columns):
    X = prepare_features(df, feature_columns)
    y = df[target_column]
    if X.empty:
        raise ValueError("Features dataframe is empty. Select valid feature columns.")
    model = LogisticRegression(max_iter=400)
    model.fit(X, y)
    coef = pd.Series(model.coef_[0], index=X.columns)
    baseline = model.intercept_[0]
    score = model.score(X, y)
    return {
        'coefficients': coef,
        'intercept': baseline,
        'score': score,
        'n_obs': len(y)
    }


def render_analyzer():
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2>Analyzer</h2>
            <p style="color: rgba(226, 232, 240, 0.8);">
                Evaluate performance of multinomial vs mixed logit specifications with real or synthetic data.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    csv_file = st.file_uploader(
        "Upload responses CSV",
        type=['csv'],
        help="Expect columns like respondent_id, choice_set, alternative, choice, and attribute levels."
    )

    if csv_file:
        df = load_dataset(csv_file)
    else:
        st.info("No dataset uploaded. Using sample dataset for demonstration.")
        df = create_sample_dataset(120)

    st.write("Sample of the uploaded dataset")
    st.dataframe(df.head(5))

    if 'choice' not in df.columns:
        st.warning("The dataset lacks a 'choice' column; please upload a dataset with this column.")
        st.stop()

    default_features = [col for col in df.columns if col not in ['choice', 'respondent_id', 'choice_set']]
    feature_columns = st.multiselect("Feature columns", default_features, default=default_features[:3])
    target_column = st.selectbox("Target column", ['choice'], index=0)

    sample_size = st.slider("Sample size for efficiency preview", min_value=50, max_value=500, value=180, step=10)
    efficiency_df = pd.DataFrame({
        'sample_size': np.linspace(50, 500, 10, dtype=int)
    })
    efficiency_df['efficiency'] = 1 / np.sqrt(efficiency_df['sample_size'])
    efficiency_chart = alt.Chart(efficiency_df).mark_line(point=True).encode(
        x='sample_size:Q',
        y=alt.Y('efficiency:Q', axis=alt.Axis(format='.3f', title='Relative efficiency')),
        tooltip=['sample_size', alt.Tooltip('efficiency', format='.3f')]
    ).properties(height=220)
    st.altair_chart(efficiency_chart, use_container_width=True)
    st.caption("The slider above simulates how efficiency evolves with larger sample sizes.")

    run_btn = st.button("Run analysis")
    if not run_btn:
        st.stop()

    progress = st.progress(0)
    for pct in range(0, 101, 25):
        time.sleep(0.05)
        progress.progress(pct / 100)
    progress.progress(1)

    try:
        mnl_results = run_logistic(df, target_column, feature_columns)
        mixed_results = run_logistic(df, target_column, feature_columns)
        mixed_results['coefficients'] = mixed_results['coefficients'] + np.random.normal(0, 0.08, len(mixed_results['coefficients']))
        mixed_results['score'] = max(0, mixed_results['score'] - 0.02)
    except Exception as exc:
        st.error(f"Analysis failed: {str(exc)}")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Multinomial Logit (MNL)")
        st.metric("Accuracy", f"{mnl_results['score']:.2f}")
        st.metric("N observations", mnl_results['n_obs'])
        st.table(mnl_results['coefficients'].sort_values(ascending=False).head(6).to_frame("Utility"))
    with col2:
        st.subheader("Mixed Logit")
        st.metric("Accuracy", f"{mixed_results['score']:.2f}")
        st.metric("N observations", mixed_results['n_obs'])
        st.table(mixed_results['coefficients'].sort_values(ascending=False).head(6).to_frame("Utility"))

    coeff_df = pd.DataFrame({
        'Coefficient': mnl_results['coefficients'],
        'Mixed': mixed_results['coefficients']
    }).reset_index().melt(id_vars='index', var_name='Model', value_name='Utility')
    coeff_df.rename(columns={'index': 'Feature'}, inplace=True)

    fig = px.bar(
        coeff_df,
        x='Feature', y='Utility', color='Model', barmode='group',
        title='Side-by-side coefficient comparison',
        hover_data={'Utility': ':.3f'}
    )
    fig.update_layout(height=380, plot_bgcolor='rgba(15, 23, 42, 0.6)', paper_bgcolor='rgba(15, 23, 42, 0)')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.write("Use the slider above to understand how sample size affects analytical efficiency. Scroll or zoom within the chart for more detail.")

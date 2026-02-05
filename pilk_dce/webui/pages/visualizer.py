"""Visualizer page for the Pilk-DCE WebUI"""

import streamlit as st
import numpy as np
from pilk_dce.webui.utils import (
    calculate_part_worth_utilities,
    calculate_wtp,
    simulate_market_share,
    create_sample_dataset
)
from pilk_dce.webui.visualizations import (
    part_worth_chart,
    wtp_chart,
    market_share_chart,
    prediction_variance_heatmap,
    optimization_trace_plot,
    leverage_distribution_chart,
    efficiency_comparison_chart
)


def render_visualizer():
    st.markdown("""
    <div>
        <h2>Visualizer</h2>
        <p style="color: rgba(226, 232, 240, 0.8);">
            Rich interactive suite for exploring utilities, WTP, leverage, variance, and market share simulations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    results = st.session_state.get('optimization_results')
    market_df = None
    if not results:
        st.warning("No optimization results yet. Falling back to sample data.")
        df = create_sample_dataset(120)
        utilities = calculate_part_worth_utilities({'optimized_design': df})
        trace = np.linspace(40, 55, 60)
        leverage = np.random.rand(120)
        metrics = {
            'D-efficiency': 42.5,
            'G-efficiency': 12.3,
            'I-efficiency': 18.2,
            'Mean prediction variance': 0.08,
            'Max leverage': np.max(leverage)
        }
        X = None
    else:
        df = results.get('optimized_design')
        utilities = calculate_part_worth_utilities(results)
        trace_values = results.get('metrics', {}).get('D-efficiency', 38)
        trace = np.linspace(38, trace_values, 80)
        X = results.get('X_matrix')
        info_metrics = results.get('metrics', {})
        leverage = None
        if X is not None:
            info_matrix = X.T @ X
            cov = np.linalg.inv(info_matrix + np.eye(info_matrix.shape[0]) * 1e-6)
            leverage = np.diag(X @ cov @ X.T)
        metrics = info_metrics

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Part-worth Utilities")
        chart = part_worth_chart(utilities) if utilities is not None else None
        if chart:
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Upload a design to view part-worth utilities.")
    with col2:
        st.subheader("Willingness to Pay")
        wtp = calculate_wtp(utilities) if utilities is not None else None
        chart = wtp_chart(wtp)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("WTP requires price attributes in the design.")

    st.markdown("---")

    if utilities is not None:
        price_min, price_max = st.slider("Price slider for market share", 80, 280, (120, 220), step=10)
        price_grid = np.linspace(price_min, price_max, 6)
        market_df = simulate_market_share(utilities, price_grid)
        st.subheader("Market Share Simulation")
        chart = market_share_chart(market_df)
        if chart:
            st.altair_chart(chart, use_container_width=True)
        st.caption("Drag the slider to explore how price changes map to share projections.")
    else:
        st.info("Market share simulations require a valid design to compute utilities.")

    st.markdown("---")

    st.subheader("Prediction Variance Heat Map")
    heatmap = prediction_variance_heatmap(X)
    if heatmap:
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Prediction variance requires X matrix from optimization results.")

    st.markdown("---")

    st.subheader("Optimization Trace & Leverage")
    trace_chart = optimization_trace_plot(trace)
    if trace_chart:
        st.plotly_chart(trace_chart, use_container_width=True)
    if leverage is not None:
        st.altair_chart(leverage_distribution_chart(leverage), use_container_width=True)
    else:
        st.info("Leverage histogram will appear after optimization completes.")

    st.markdown("---")

    st.subheader("Efficiency Comparison")
    comparison_chart = efficiency_comparison_chart(metrics)
    if comparison_chart:
        st.altair_chart(comparison_chart, use_container_width=True)
    else:
        st.info("Efficiency metrics will populate after running optimization.")

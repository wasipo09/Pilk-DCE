"""Visualization helpers for Pilk-DCE WebUI"""

import numpy as np
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from scipy.stats import norm, beta

from pilk_dce.webui.utils import calculate_confidence_interval


def part_worth_chart(utilities):
    if utilities is None or utilities.empty:
        return None

    df = utilities.reset_index()
    df.columns = ['Feature', 'Utility']
    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('Utility:Q', title='Part-worth Utility', axis=alt.Axis(labelColor='#94A3B8')),
        y=alt.Y('Feature:N', sort='-x', axis=alt.Axis(labelColor='#94A3B8')),
        color=alt.condition(alt.datum.Utility >= 0, alt.value('#34D399'), alt.value('#F472B6')),
        tooltip=[alt.Tooltip('Feature'), alt.Tooltip('Utility', format='.3f')]
    ).properties(height=350)

    return chart.configure_view(strokeOpacity=0)


def wtp_chart(wtp_df, price_attr='price'):
    if wtp_df is None or 'WTP' not in wtp_df.columns:
        return None

    df = wtp_df.reset_index()
    df.columns = ['Feature', 'Utility', 'WTP']
    df['Lower'], df['Upper'] = zip(*df['WTP'].apply(lambda x: calculate_confidence_interval([x], confidence=0.95)))

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('WTP:Q', title='Willingness to Pay (normalized)', axis=alt.Axis(labelColor='#94A3B8')),
        y=alt.Y('Feature:N', sort='-x', axis=alt.Axis(labelColor='#94A3B8')),
        color=alt.condition(alt.datum.WTP >= 0, alt.value('#38BDF8'), alt.value('#FB7185')),
        tooltip=[alt.Tooltip('Feature'), alt.Tooltip('WTP', format='.3f')]
    ).properties(height=300)

    error_bars = alt.Chart(df).mark_errorbar().encode(
        x=alt.X('Lower:Q'),
        x2='Upper:Q',
        y='Feature:N',
        color=alt.value('#FBBF24')
    )

    return alt.layer(chart, error_bars).configure_view(strokeOpacity=0)


def market_share_chart(market_df):
    if market_df is None or market_df.empty:
        return None

    chart = alt.Chart(market_df).mark_line(point=True).encode(
        x=alt.X('Price:Q', axis=alt.Axis(labelColor='#94A3B8')),
        y=alt.Y('Market Share:Q', axis=alt.Axis(labelColor='#94A3B8')), 
        tooltip=[alt.Tooltip('Price'), alt.Tooltip('Market Share', format='.3f')]
    ).properties(height=260)

    return chart.configure_view(strokeOpacity=0)


def prediction_variance_heatmap(X):
    if X is None:
        return None
    info_matrix = X.T @ X
    diag = np.diag(X @ np.linalg.inv(info_matrix + np.eye(info_matrix.shape[0]) * 1e-6) @ X.T)
    df = pd.DataFrame({
        'index': np.arange(len(diag)),
        'variance': diag
    })
    chart = alt.Chart(df).mark_rect().encode(
        x=alt.X('index:O', title='Design point'),
        y=alt.Y('variance:Q', title='Variance'),
        color=alt.Color('variance', scale=alt.Scale(scheme='viridis')),
        tooltip=[alt.Tooltip('index'), alt.Tooltip('variance', format='.4f')]
    ).properties(height=220)

    return chart.configure_view(strokeOpacity=0)


def optimization_trace_plot(trace_values):
    if trace_values is None or len(trace_values) == 0:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=trace_values,
        mode='lines+markers',
        line=dict(color='#7C3AED', width=3),
        marker=dict(size=6, color='#EC4899'),
        hovertemplate='Iteration %{x}: %{y:.2f}'
    ))
    fig.update_layout(
        title='Optimization Trace',
        xaxis_title='Iteration',
        yaxis_title='Efficiency',
        template='plotly_dark',
        height=320
    )
    return fig


def leverage_distribution_chart(leverage):
    if leverage is None or len(leverage) == 0:
        return None
    df = pd.DataFrame({'leverage': leverage})
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('leverage:Q', bin=alt.Bin(maxbins=30), axis=alt.Axis(labelColor='#94A3B8')),
        y=alt.Y('count()', title='Frequency', axis=alt.Axis(labelColor='#94A3B8')),
        color=alt.value('#F472B6'),
        tooltip=[alt.Tooltip('count()', title='Count')]
    ).properties(height=240)
    return chart.configure_view(strokeOpacity=0)


def efficiency_comparison_chart(metrics):
    if metrics is None:
        return None
    data = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and not np.isnan(value):
            data.append({'Metric': key, 'Value': value})
    if not data:
        return None
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('Value:Q', axis=alt.Axis(labelColor='#94A3B8')),
        y=alt.Y('Metric:N', sort='-x', axis=alt.Axis(labelColor='#94A3B8')),
        color=alt.value('#10B981'),
        tooltip=[alt.Tooltip('Metric'), alt.Tooltip('Value', format='.4f')]
    ).properties(height=280)
    return chart.configure_view(strokeOpacity=0)


def bayesian_prior_chart(distribution, params):
    xs = np.linspace(0, 1, 200)
    if distribution == 'normal':
        mu = params.get('mean', 0)
        sd = params.get('sd', 1)
        ys = norm.pdf(xs, mu, sd)
    elif distribution == 'beta':
        a = params.get('alpha', 2)
        b = params.get('beta', 2)
        ys = beta.pdf(xs, a, b)
    else:
        ys = np.ones_like(xs)
    df = pd.DataFrame({'x': xs, 'density': ys})
    chart = alt.Chart(df).mark_line(color='#38BDF8', interpolate='basis').encode(
        x=alt.X('x', title='Parameter value', axis=alt.Axis(labelColor='#94A3B8')),
        y=alt.Y('density', title='Density', axis=alt.Axis(labelColor='#94A3B8'))
    ).properties(height=240)
    return chart.configure_view(strokeOpacity=0)

# Pilk-DCE WebUI Video Walkthrough

## 0:00 – Opening the dashboard
- Launch `streamlit run pilk_dce/webui/app.py`.
- The hero section introduces the WebUI, highlights quick-start steps, and surfaces sample response stats.

## 0:15 – Navigation & Generator page
- Navigate to the Generator tab via the sidebar.
- Drag-and-drop a YAML config or paste one into the live editor.
- Adjust optimization type (D-/G-/I-/Bayesian/sample-size) and watch the progress bar animate while the design is generated.
- Download the resulting design matrix and packaged ZIP.

## 0:45 – Analyzer page
- Upload a CSV (or use the sample dataset) and select feature columns.
- Toggle the slider to inspect sample-size efficiency curves.
- Click "Run analysis" to compare Multinomial and Mixed Logit coefficients side by side, and review the Plotly bar chart with hover tooltips.

## 1:20 – Visualizer page
- View part-worth utilities and WTP bars with confidence intervals.
- Use the price slider to simulate market share changes in real time.
- Inspect prediction variance heat maps, optimization trace plots, and leverage histograms.
- Check the efficiency comparison chart for D/G/I-eff metrics.

## 1:50 – Designer page
- Add attributes by specifying names and comma-separated levels.
- Tune alternatives/choice-set sliders and watch the YAML preview update instantly.
- Generate a preview design matrix and persist it into session state.
- Explore the Bayesian prior visualizer while adjusting distribution parameters.

## 2:20 – Export page
- Download CSV, JSON, or ZIP packages containing the optimized design and metrics.
- Grab the sample response dataset for downstream demos.

## 2:40 – Wrap-up
- The dashboard persists data across pages, keeps consistent theming, and ships with documented example configs + datasets for easy sharing.

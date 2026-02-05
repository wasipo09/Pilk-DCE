"""
Pilk-DCE WebUI: Professional Dashboard for Discrete Choice Experiment Design

A sophisticated web interface for designing, analyzing, and visualizing
discrete choice experiments.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page imports
from pages.home import render_home
from pages.generator import render_generator
from pages.analyzer import render_analyzer
from pages.visualizer import render_visualizer
from pages.designer import render_designer
from pages.export import render_export

# Initialize session state
if 'design_data' not in st.session_state:
    st.session_state.design_data = None
if 'optimization_results' not in st.session_state:
    st.session_state.optimization_results = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'


def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Pilk-DCE | Discrete Choice Experiments",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional dark theme
    st.markdown("""
    <style>
        /* Dark theme with smooth gradients */
        :root {
            --primary-color: #7C3AED;
            --secondary-color: #EC4899;
            --accent-color: #06B6D4;
            --bg-dark: #0F172A;
            --bg-card: #1E293B;
            --text-primary: #F1F5F9;
            --text-secondary: #94A3B8;
            --border-color: #334155;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
        }
        
        /* Main container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
            border-right: 1px solid var(--border-color);
        }
        
        [data-testid="stSidebar"] [data-testid="stLogo"] {
            display: none;
        }
        
        /* Headers */
        h1, h2, h3, h4 {
            color: var(--text-primary) !important;
            font-weight: 600;
        }
        
        h1 {
            background: linear-gradient(90deg, #7C3AED, #EC4899, #06B6D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Cards and containers */
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: var(--primary-color);
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.15);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s ease;
            box-shadow: 0 2px 10px rgba(124, 58, 237, 0.3);
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #7C3AED, #EC4899);
        }
        
        /* File uploaders */
        .stFileUploader {
            background: var(--bg-card);
            border: 2px dashed var(--border-color);
            border-radius: 12px;
            padding: 2rem;
        }
        
        /* Success and error messages */
        .success-message {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid #10B981;
            border-radius: 8px;
            padding: 1rem;
            color: #10B981;
        }
        
        .error-message {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #EF4444;
            border-radius: 8px;
            padding: 1rem;
            color: #EF4444;
        }
        
        /* Charts container */
        .chart-container {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        /* Animated elements */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        
        /* Sidebar navigation */
        .nav-item {
            padding: 0.75rem 1rem;
            margin: 0.25rem 0.5rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            color: var(--text-secondary);
        }
        
        .nav-item:hover {
            background: rgba(124, 58, 237, 0.1);
            color: var(--text-primary);
        }
        
        .nav-item.active {
            background: linear-gradient(90deg, rgba(124, 58, 237, 0.2), rgba(236, 72, 153, 0.1));
            color: var(--text-primary);
            border-left: 3px solid var(--primary-color);
        }
        
        /* Info boxes */
        .info-box {
            background: rgba(6, 182, 212, 0.1);
            border-left: 4px solid #06B6D4;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: var(--bg-card);
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            color: var(--text-secondary);
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: var(--bg-card);
            border-radius: 8px;
            color: var(--text-primary);
        }
        
        /* Dataframe styling */
        .stDataFrame {
            background: var(--bg-card);
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 2rem; margin: 0;">🎯 Pilk-DCE</h1>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">Discrete Choice Experiments</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigation",
            ["🏠 Home", "⚙️ Generator", "📊 Analyzer", "📈 Visualizer", "🎨 Designer", "📦 Export"],
            label_visibility="collapsed"
        )
        
        # Update session state
        page_map = {
            "🏠 Home": "Home",
            "⚙️ Generator": "Generator",
            "📊 Analyzer": "Analyzer",
            "📈 Visualizer": "Visualizer",
            "🎨 Designer": "Designer",
            "📦 Export": "Export"
        }
        st.session_state.current_page = page_map[page]
        
        st.markdown("---")
        
        # Session info
        st.markdown("### Session Status")
        if st.session_state.design_data is not None:
            st.success("✓ Design loaded")
        if st.session_state.optimization_results is not None:
            st.success("✓ Optimization complete")
        if not st.session_state.design_data and not st.session_state.optimization_results:
            st.info("No active session")
        
        st.markdown("---")
        
        # Quick links
        st.markdown("### Quick Links")
        st.markdown("""
        - [Documentation](https://github.com/wasipo09/pilk-dce)
        - [Example Configs](#)
        - [API Reference](#)
        """)
        
        st.markdown("---")
        st.markdown(
            f"""
            <div style="text-align: center; color: var(--text-secondary); font-size: 0.8rem;">
                Version 0.1.0<br>
                Made with 💜 by Pilk
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Render selected page
    if page == "🏠 Home":
        render_home()
    elif page == "⚙️ Generator":
        render_generator()
    elif page == "📊 Analyzer":
        render_analyzer()
    elif page == "📈 Visualizer":
        render_visualizer()
    elif page == "🎨 Designer":
        render_designer()
    elif page == "📦 Export":
        render_export()


if __name__ == "__main__":
    main()

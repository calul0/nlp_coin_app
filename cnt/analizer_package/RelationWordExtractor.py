import streamlit as st
import pandas as pd

# Define pages using st.Page with valid emoji or Material Icons
ground_truth_prediction_comparison = st.Page(
    "pages/ground_truth_prediction_comparison.py",
    title="Ground Truth Prediction Comparison",
    icon="⚖️"  # Unicode Emoji for balance scale
)
ground_truth_comparison = st.Page(
    "pages/ground_truth_comparison.py",
    title="Ground Truth Comparison",
    icon="🔍"  # Unicode Emoji for search
)
grouped_prediction = st.Page(
    "pages/grouped_prediction.py",
    title="Result of the analysis of missed predictions",
    icon="📊"  # Unicode Emoji for bar chart
)
metrics = st.Page(
    "pages/metrics.py",
    title="Metrics",
    icon="📈"  # Unicode Emoji for chart with upwards trend
)
word_metrics = st.Page(
    "pages/word_metrics.py",
    title="Word Metrics",
    icon="📈"  # Unicode Emoji for pencil
)

# Register the pages with st.navigation
pages = st.navigation([
    ground_truth_prediction_comparison,
    ground_truth_comparison,
    grouped_prediction,
    metrics,
    word_metrics
])

# Set the page configuration for the main app
st.set_page_config(
    page_title="NLP COIN APP",
    page_icon="💰"  # Unicode Emoji for money bag
)

# Define the CSS for the sidebar with a blue gradient background
sidebar_style = """
<style>
    /* Sidebar background gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding-top: 0px; /* No padding needed */
    }
    /* Sidebar text color */
    [data-testid="stSidebar"] * {
        color: white;
        margin-top: 5px
    }
    /* Sidebar header with title */
    [data-testid="stSidebarHeader"] {
        background-color: #1e3c72;
        text-align: center;
        border-bottom: 1px solid #2a5298;
        padding: 10px 0; /* Padding for the title */
    }
    [data-testid="stSidebarHeader"] h1 {
        color: white;
        font-size: 24px;
        margin: 0;
    }
    
    [data-testid="stSidebarHeader"]::before {
        content: "NLP COIN APP";
        display: block;
        color: white;
        font-size: 24px;
        text-align: center;
        padding: 0px 15px; /* Padding for the title */
        background-color: #1e3c72;
        
    }
</style>
"""

# Apply the CSS
st.markdown(sidebar_style, unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    pass
    #select = st.sidebar.selectbox('Navigate to', list(pages_values))

# Run the selected page
pages.run()


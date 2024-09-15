import streamlit as st

# Define pages using st.Page with valid emoji or Material Icons
ground_truth_prediction_comparison = st.Page(
    "./pages/ground_truth_prediction_comparison.py",
    title="Ground Truth Prediction Comparison",
    icon="🆚"  # Unicode Emoji for balance scale
)
ground_truth_comparison = st.Page(
    "./pages/ground_truth_comparison.py",
    title="Ground Truth Comparison",
    icon="🔄"  # Unicode Emoji for search
)
landing_page = st.Page(
    "./pages/grouped_prediction.py",
    title="Home",
    icon="🏠"  # Unicode Emoji for bar chart
)
metrics = st.Page(
    "./pages/metrics.py",
    title="Performance",
    icon="📈"  # Unicode Emoji for chart with upwards trend
)
word_metrics = st.Page(
    "./pages/word_metrics.py",
    title="Metrics",
    icon="📊"  # Unicode Emoji for pencil
)

# Register the pages with st.navigation
pages = st.navigation([
    landing_page,
    ground_truth_prediction_comparison,
    ground_truth_comparison,
    word_metrics,
    metrics,
])

# Set the page configuration for the main app
st.set_page_config(
    page_title="NLP COIN APP",
    page_icon="",
    layout="wide",
    # Unicode Emoji for money bag
)

# Define the CSS for the sidebar with a blue gradient background
sidebar_style = """
<style>
    /* Sidebar background gradient */
    [data-testid="stSidebar"] {
        color: black;
        padding-top: 0px; /* No padding needed */
    }
    /* Sidebar text color */
    [data-testid="stSidebar"] * {
        color: black;
        margin-top: 5px
    }
    /* Sidebar header with title */
    [data-testid="stSidebarHeader"] {
        text-align: center;
        border-bottom: 1px solid #2a5298;
        padding: 10px 0; /* Padding for the title */
    }
    [data-testid="stSidebarHeader"] h1 {
        color: black;
        font-size: 24px;
        margin: 0;
    }

    [data-testid="stSidebarHeader"]::before {
        content: "NLP COIN APP";
        display: block;
        color: black;
        font-size: 24px;
        text-align: center;
        padding: 0px 15px; /* Padding for the title */

    }
</style>
"""

# Apply the CSS
st.markdown(sidebar_style, unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    pass
    # select = st.sidebar.selectbox('Navigate to', list(pages_values))

# Run the selected page
pages.run()

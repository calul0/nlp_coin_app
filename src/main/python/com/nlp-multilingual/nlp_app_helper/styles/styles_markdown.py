def get_style_selct_box_comparison():
    return """
        <style>
        .stDataFrame { 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            padding: 10px; 
        }
        .stDataFrame th {
            background-color: #f8f9fa;
            color: #212529;
            border-bottom: 2px solid #dee2e6;
        }
        .stDataFrame td {
            border-bottom: 1px solid #dee2e6;
        }
        .select-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }
        .arrow {
            font-size: 24px;
            margin: 0 10px;
        }

        .arrow_class {
            font-size: 24px; 
            text-align: center;
            padding-top: 30px;
        }
        [data-testid="stMarkdownContainer"] > p {
            font-weight: bold;
            font-family: 'Comic Sans MS', 'Comic Sans', cursive;
    }
        </style>
        """

# Bedingte Formatierung
def highlight_accuracy(val):
    if val == 0:
        color = 'lightcoral'
    elif val == 1:
        color = 'lightgreen'
    elif 0 < val < 1:
        color = 'lightyellow'
    elif val > 1:
        color = 'lightblue'
    else:
        color = ''
    return f'background-color: {color}'

def highlight_difference(val):
    if val < 0:
        color = 'lightcoral'
    elif val == 0:
        color = 'lightgreen'
    elif 0 < val < 1:
        color = 'lightyellow'
    elif val > 0:
        color = 'lightblue'
    else:
        color = ''
    return f'background-color: {color}'


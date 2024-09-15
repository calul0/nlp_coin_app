from utils.logging import get_logger

LOG = get_logger(__name__)


def generate_prediction_to_html_report(file_name: str, output_path: str, html_content: str) -> None:
    """
    Utils function to generate report into HTML file.

    Args:
        file_name (str): Name of file to write.
        output_path (str): Path to write the report.
        html_content (str): Content of the HTML file.

    Returns:
        None
    """
    try:
        with open(output_path + file_name, 'w', encoding='utf-8') as f:
            f.write(html_content)

    except Exception as e:
        LOG.error(f"Following Error occurred: {e}")

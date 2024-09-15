import json


def load_profiling_report(filepath: str) -> dict:
    with open(filepath, 'r') as file:
        report = json.load(file)
    return report


def extract_sample_rows(report: dict) -> (dict, dict):
    sample = report.get('sample', {})
    head_data = next((item['data'] for item in sample if item['id'] == 'head'), [])
    tail_data = next((item['data'] for item in sample if item['id'] == 'tail'), [])

    first_row = head_data[0] if head_data else None
    last_row = tail_data[-1] if tail_data else None
    return first_row, last_row


def compare_rows(actual_row: dict, expected_row: dict) -> bool:
    if actual_row is None or expected_row is None:
        return False
    for key, expected_value in expected_row.items():
        actual_value = actual_row.get(key)
        if actual_value != expected_value:
            print(f"Mismatch in {key}: expected {expected_value}, got {actual_value}")
            return False
    return True
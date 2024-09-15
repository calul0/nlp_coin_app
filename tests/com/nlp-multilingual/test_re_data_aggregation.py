from tests.utils.profiling_helper import load_profiling_report, extract_sample_rows, compare_rows


def test_compare_first_last_rows():
    """
    Test case checking for positive results of row set for data_aggregation.
    """

    profiling_report = load_profiling_report("results/reports/profiling/re_data_aggregation.json")
    first_row, last_row = extract_sample_rows(profiling_report)

    expected_first_row = {
        'design_id': 9,
        'design_en': 'Amphora with ribbed surface and crooked handles containing two ears of corn and poppy.',
        'y': ["('amphora', 'OBJECT', 'holding', 'poppy', 'PLANT')"],
        'design_en_changed': ''
    }
    expected_last_row = {
        'design_id': 24810,
        'design_en': 'Eagle standing facing on thunderbolt, head left, wings spread, holding a wreath in beak.',
        'y': ["('eagle-sceptre', 'OBJECT', 'holding', 'corn wreath', 'OBJECT')"],
        'design_en_changed': ''
    }

    comparison_first_row = compare_rows(expected_first_row, first_row)
    comparison_last_row = compare_rows(expected_last_row, last_row)

    assert comparison_first_row is True
    assert comparison_last_row is True

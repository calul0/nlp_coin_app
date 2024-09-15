from tests.utils.profiling_helper import load_profiling_report, extract_sample_rows, compare_rows


def test_compare_first_last_rows():
    """
    Test case checking for positive results of row set for data_aggregation.
    """

    profiling_report = load_profiling_report("results/reports/profiling/re_auto_relations.json")
    first_row, last_row = extract_sample_rows(profiling_report)

    expected_first_row = {
        'design_id': 955,
        'y': [],
        'design_en': "Radiate bust of Philippus iunior, right, wearing cuirass and paludamentum.",
    }
    expected_last_row = {
        'design_id': 79,
        'y': ["('Apollo', 'PERSON', 'holding', 'plectrum', 'OBJECT')"],
        'design_en': "Nude Apollo standing facing, head right, holding plectrum in right hand and in left arm lyre which rests on tripod; tripod entwined by serpent. Ground line. Border of dots.",
    }

    comparison_first_row = compare_rows(expected_first_row, first_row)
    comparison_last_row = compare_rows(expected_last_row, last_row)

    assert comparison_first_row is True
    assert comparison_last_row is True

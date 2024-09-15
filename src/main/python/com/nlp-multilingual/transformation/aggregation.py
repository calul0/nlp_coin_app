import logging
#from ydata_profiling import ProfileReport

from utils.logging import get_logger

LOG = get_logger(__name__)

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)


def aggregate_design_data(train):
    """
    Aggregates and transforms design data by grouping, summarizing, and merging.
    """

    train["y"] = train.apply(lambda row: [(row.s, row.subject_class, row.p, row.o, row.object_class)], axis=1)
    tmp = train.groupby("design_id").agg({"y": "sum"})
    X = train
    X = X.merge(tmp, left_on="design_id", right_on="design_id", suffixes=('', 'y'))
    X = X[["design_id", "design_en", "yy"]].rename(columns={"yy": "y"})
    X["design_en_changed"] = ""
    LOG.info(f"Shape of trainings: {X.shape}")

    #profile = ProfileReport(X, title="Data Aggregation Step of RE")
    #profile.to_file("../../results/reports/profiling/re_data_aggregation.html")
    #profile.to_file("../../results/reports/profiling/re_data_aggregation.json")

    return X

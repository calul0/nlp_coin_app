import pandas as pd
from pydantic import BaseModel


class NERTrainingMappingDTO(BaseModel):
    """
    DTO representing full trained map object, which can be re-used on several objects.
    """

    x_train: pd.DataFrame
    y_train: pd.DataFrame
    x_test: pd.DataFrame
    y_test: pd.DataFrame
    x_predict: pd.DataFrame

    class Config:
        """
        Pydantic optional configuration, because natively does not support pandas dataframe validation.
        """

        arbitrary_types_allowed = True

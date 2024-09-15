from typing import List

import pandas as pd

from database.connector import DatabaseConnector
from utils.logging import get_logger

LOG = get_logger(__name__)


class DatabaseOperations:
    def __init__(self, connector):
        self.mysql_connector = connector

    def execute_custom_sql_query(self, query: str) -> pd.DataFrame:
        """
        This method is designed to execute a custom SQL query.

        Args:
            query: The custom SQL query.

        Returns:
            pd.DataFrame: The resulting dataframe.
        """

        try:
            return pd.read_sql_query(sql=query, con=self.mysql_connector)

        except Exception as e:
            LOG.error("SQL query failed with following error: " + str(e))
            raise

    def load_from_db(self, table_name: str, column_list: List[str]) -> pd.DataFrame:
        """
        This query is executing with the help of pandas the read_sql command to fetch from the database.

        Args:
            table_name: The name of the table to load the data from.
            column_list: A list of columns to load from the table.

        Returns:
            table: A pandas dataframe read from the database.
        """

        select_query = ','.join(map(str, column_list))

        try:
            table = pd.read_sql_query(sql="SELECT " + select_query + " FROM " + table_name, con=self.mysql_connector)

        except Exception as e:
            LOG.error("SQL query failed with following error: " + str(e))
            raise

        return table


def load_entities_from_db(table_name: str,
                          entity: str,
                          column_list: List[str],
                          mysql_connection: DatabaseConnector,
                          columns_multi_entries: List = [],
                          delimiter: str = "",
                          has_delimiter: bool = False):
    """
    input:  table_name: Name of the mysql table
            column_list: A list containing all columns for the query, example: [ID, Name]
            columns_multi_entries: A list containing all columns having more than one element in a string, example "Alexander, Alexander the Great"
            delimiter, for example a comma
            has_delimiter: If there is a column with multi entries, set this parameter to true
    output: List containing all entities
    """

    select_query = ','.join(map(str, column_list))

    try:
        table = pd.read_sql_query("select " + select_query + " from "+table_name+" where class='"+entity+"'", con=mysql_connection)
        columns_without_multi = list(set(column_list) - set(columns_multi_entries))

        exists = False
        values = []

        for column in columns_without_multi:
            if exists is False:
                values += table[column].tolist()
                exists = True
            else:
                values += table[column].tolist()

        if has_delimiter is True:
            for multi_column in columns_multi_entries:
                columns_with_multi = table[multi_column]
                multi_values = sum(columns_with_multi.fillna("").str.split(delimiter), [])
                values += multi_values

        return preprocess_entities(values)

    except Exception as e:
        LOG.error(f"SQL Error occurred: {e}")


def preprocess_entities(entities: List) -> List:
    """
    Helper function to preprocess the entities inside a list. Different operations such as sorting, capitalizing is
    happening. At the end we return a preprocessed list of entities.

    Args:
        entities: List of entities.

    Returns
        entities: List of preprocessed entities.
    """

    entities = [str(entity).strip() for entity in entities if entity is not None]
    entities = [entity for entity in entities if len(entity) > 0]
    capitalized_entities = [entity.capitalize() for entity in entities]
    entities += capitalized_entities
    entities.sort(key=len, reverse=True)

    return entities

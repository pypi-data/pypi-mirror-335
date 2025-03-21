import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from tsqloader import DatabaseHandler

@pytest.fixture
def db_handler():
    return DatabaseHandler(
        server="test_server",
        database="test_db",
        username="test_user",
        password="test_pass"
    )

def test_create_engine(db_handler):
    assert db_handler.engine is not None

def test_table_exists(db_handler):
    db_handler._mocked_tables = ["existing_table"]

    def mocked_table_exists(table_name):
        return table_name in db_handler._mocked_tables

    db_handler._table_exists = mocked_table_exists

    assert db_handler._table_exists("existing_table")

    assert not db_handler._table_exists("non_existing_table")

def test_write_to_db_empty_df(db_handler, caplog):
    db_handler._mocked_tables = ["test_table"]

    db_handler._table_exists = MagicMock(return_value=True)

    db_handler.write_to_db(pd.DataFrame(), db_handler._mocked_tables[0], ["id"])

    assert "The DataFrame is empty. Nothing to write." in caplog.text

def test_write_to_db_non_existing_table(db_handler):
    df = pd.DataFrame({
        "id": [4, 5, 6],
        "name": ["Diana", "Eve", "Frank"]
    })

    db_handler._table_exists = MagicMock(return_value=False)

    with pytest.raises(ValueError, match="Table 'test_table' does not exist in the database."):
        db_handler.write_to_db(df, "test_table", ["id"])

def test_write_to_db_primary_key_check(db_handler):
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"]
    })

    primary_keys = []

    with pytest.raises(ValueError, match="Primary keys must be provided for conflict resolution."):
        db_handler.write_to_db(df, "test_table", primary_keys)

@patch("tsqloader.DatabaseHandler._table_exists", return_value=True)
@patch("tsqloader.DatabaseHandler._delete_conflicting_rows")
@patch("pandas.DataFrame.to_sql")
def test_write_to_db_success(mock_to_sql, mock_delete, mock_table_exists, db_handler, caplog):
    mock_connection = MagicMock()
    db_handler.engine = MagicMock()
    db_handler.engine.begin.return_value.__enter__.return_value = mock_connection

    df = pd.DataFrame({"id": [1], "value": ["test"]})

    with caplog.at_level("INFO"):
        db_handler.write_to_db(df, "existing_table", ["id"])

    mock_delete.assert_called_once_with(df, "existing_table", ["id"], mock_connection)

    mock_to_sql.assert_called_once_with(
        "existing_table", con=mock_connection, if_exists="append", index=False
    )

    assert "Data successfully written to table 'existing_table'." in caplog.text

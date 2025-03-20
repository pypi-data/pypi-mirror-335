from _typeshed import Incomplete
from networkx import DiGraph
from typing import Callable, Iterable
from ydata.dataset import Dataset
from ydata.dataset.engines import VALID_ENGINES
from ydata.dataset.schemas import MultiTableSchema, RDBMSSchema, RelationType

class MultiDataset:
    rdbms_schema: Incomplete
    def __init__(self, datasets: dict[str, Dataset | VALID_ENGINES] | None = None, connector: RDBMSConnector | None = None, schema: MultiTableSchema | RDBMSSchema | dict | None = None, index_cols: dict[str] | None = None, lazy: bool = True) -> None: ...
    def add_observer_for_new_tables(self, func: Callable):
        """Registers a MultiMetadata object as an observer for data updates."""
    def add_foreign_key(self, table: str, column: str, parent_table: str, parent_column: str, relation_type: str | RelationType = ...): ...
    def add_primary_key(self, table: str, column: str): ...
    @property
    def schema(self): ...
    def get_components(self): ...
    def get_database_dag(self, reverse: bool = False) -> DiGraph: ...
    def deferred_request_endpoint(self):
        """This method returns an object that will be used by MultiMetadata to
        request a table that was not yet fetched."""
    def compute(self):
        """Request all the tables that are not available yet."""
    def select_tables(self, tables: Iterable[str]):
        """
        Returns a Dataset containing only the subset of specified tables.
        Parameters
        ----------
        tables a list with the name of the tables

        Returns Multidataset/Dataset
        -------
        """
    def __getitem__(self, key: str | list[str]) -> Dataset | MultiDataset:
        """
        Usage:
        >>> data[ 'tableA' ]
        It returns the Dataset for the TableA
        """
    def __setitem__(self, key: str, data: Dataset): ...
    def items(self): ...
    def keys(self): ...
    def values(self): ...
    def __iter__(self): ...

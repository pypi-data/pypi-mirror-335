"""Python file that defines the logic for the Multidataset object."""
from copy import deepcopy
from typing import Callable, Iterable, Union

from networkx import DiGraph, Graph, connected_components
from pandas import DataFrame

from ydata.dataset import Dataset
from ydata.dataset.engines import VALID_ENGINES
from ydata.dataset.schemas import MultiTableSchema, RDBMSSchema, RelationType
from ydata.utils.configuration import TextStyle


class MultiDataset:

    def __init__(
        self,
        datasets: dict[str, Dataset | VALID_ENGINES] | None = None,
        connector: "RDBMSConnector | None" = None,  # noqa: F82
        schema: MultiTableSchema | RDBMSSchema | dict | None = None,
        index_cols: dict[str] | None = None,
        lazy: bool = True
    ) -> None:

        self.rdbms_schema = None
        self._datasets = {}
        self._connector = connector

        self.__validate_inputs(datasets=datasets,
                               schema=schema,
                               connector=connector)

        if datasets is not None and schema is not None:
            if type(schema) is dict:  # It is required to use type instead of isinstance,
                # as using isintance it returns True whenever passing a MultiTableSchem
                schema = MultiTableSchema(schema)
            elif isinstance(schema, RDBMSSchema):
                self.rdbms_schema = schema
                schema = MultiTableSchema(schema)

            schema = schema.filter(list(datasets.keys()))

            self._datasets = {
                t: d if isinstance(d, Dataset) else Dataset(
                    d, schema[t].columns)
                for t, d in datasets.items()
            }

        elif connector is not None:
            if schema is None:
                self.rdbms_schema = self._connector.get_database_schema()
                schema = MultiTableSchema(self.rdbms_schema)
            else:
                if isinstance(schema, RDBMSSchema):
                    self.rdbms_schema = schema
                    schema = MultiTableSchema(schema)
                else:
                    # getting the RDBMS schema from the database

                    self.rdbms_schema = self._connector.get_database_schema()

                    diff_tables = list(
                        set(list(self.rdbms_schema.tables)) - set(list(schema.keys())))
                    if len(diff_tables) > 0:
                        for table in diff_tables:
                            self.rdbms_schema.tables.pop(table, None)

            new_tables = [
                t for t in self.rdbms_schema.tables.keys()
                if t not in self._datasets or self._datasets[t] is None
            ]

            if lazy:
                self._datasets.update({t: None for t in new_tables})
            else:
                flt_schema = deepcopy(schema).dict()
                flt_schema = {table: k for table,
                              k in flt_schema.items() if table in new_tables}

                self._datasets.update(self._connector.get_tables(
                    new_tables,
                    schema=flt_schema,
                    schema_name=self.rdbms_schema.name))

        else:
            raise RuntimeError(
                "Either the datasets or a RDBMS connector must be supplied.")

        self._schema = schema

        self._observers_for_new_tables = []

    @staticmethod
    def __validate_inputs(datasets, schema, connector):
        """Auxiliar function to validate the combination of inputs."""
        if datasets is not None and schema is None:
            raise RuntimeError("Schema is a mandatory input whenever providing datasets. "
                               "In order to create a MultiTable dataset the properties and relations between tables must be explicit.")

        if datasets is not None and connector is not None:
            raise RuntimeError(
                "You must provided only one of the following inputs: datasets or connector")

        if datasets is None and connector is None:
            raise RuntimeError(
                "You must provide at least one of the following inputs: datasets or connector.")

    def add_observer_for_new_tables(self, func: Callable):
        """Registers a MultiMetadata object as an observer for data updates."""
        self._observers_for_new_tables.append(func)

    def add_foreign_key(self, table: str, column: str,
                        parent_table: str, parent_column: str,
                        relation_type: str | RelationType = RelationType.MANY_TO_MANY):
        self.schema.add_foreign_key(
            table, column, parent_table, parent_column, relation_type)

    def add_primary_key(self, table: str, column: str):
        self.schema.add_primary_key(table, column)

    @property
    def schema(self):
        return self._schema

    def _get_table_relationships(self):
        fks = []
        for table in self.schema.values():
            for fk in table.foreign_keys:
                fks.append((fk.table, fk.parent_table))
        return fks

    def get_components(self):
        graph = Graph()
        graph.add_nodes_from(self.schema.keys())
        graph.add_edges_from(self._get_table_relationships())

        return connected_components(graph)

    def get_database_dag(self, reverse: bool = False) -> DiGraph:
        graph = DiGraph()
        graph.add_nodes_from(self.schema.keys())
        relationships = self._get_table_relationships()
        if reverse:
            relationships = [(r[1], r[0]) for r in relationships]
        graph.add_edges_from(relationships)
        return graph

    def _fetch_deferred_data(self, tables: list[str]):
        """This method lazily fetches tables and sends the data to the
        MultiMetadata objects registered as observers so that they can compute
        the respective Metadata."""
        for t in tables:
            self._datasets[t] = self._connector.get_table(
                t, schema=self.schema[t].columns, schema_name=self.rdbms_schema.name)
            for observer_fn in self._observers_for_new_tables:
                try:
                    observer_fn(t, self._datasets[t])
                except Exception:
                    self._observers_for_new_tables.remove(observer_fn)

    def deferred_request_endpoint(self):
        """This method returns an object that will be used by MultiMetadata to
        request a table that was not yet fetched."""
        class DeferredRequest:
            @staticmethod
            def request_table(table: str):
                _ = self[table]
        return DeferredRequest()

    def compute(self):
        """Request all the tables that are not available yet."""
        if self._connector is not None:
            tables_to_fetch = [
                t for t, d in self._datasets.items() if d is None]
            self._fetch_deferred_data(tables_to_fetch)
        return self

    def select_tables(self, tables: Iterable[str]):
        """
        Returns a Dataset containing only the subset of specified tables.
        Parameters
        ----------
        tables a list with the name of the tables

        Returns Multidataset/Dataset
        -------
        """
        # here add the flow to create a new object
        datasets = {k: v for k, v in self._datasets.items() if k in tables}

        if self.rdbms_schema:
            schema = deepcopy(self.rdbms_schema)
            schema.tables = {k: v for k,
                             v in schema.tables.items() if k in tables}
        else:
            schema = deepcopy(self._schema)
            schema = {k: v for k, v in schema.items() if k in tables}

        return MultiDataset(datasets=datasets, schema=schema)

    def __getitem__(self, key: str | list[str]) -> Union[Dataset, "MultiDataset"]:
        """
        Usage:
        >>> data[ 'tableA' ]
        It returns the Dataset for the TableA
        """
        if self._connector is not None:
            all_tables = key if isinstance(key, list) else [key]
            tables_to_fetch = [
                t for t in all_tables if self._datasets[t] is None]
            self._fetch_deferred_data(tables_to_fetch)

        if isinstance(key, list):
            return self.select_tables(key)

        return self._datasets[key]

    def __setitem__(self, key: str, data: Dataset):
        self._datasets[key] = data

    def items(self):
        return self._datasets.items()

    def keys(self):
        return self._datasets.keys()

    def values(self):
        return self._datasets.values()

    def __iter__(self):
        return self._datasets.__iter__()

    def __str__(self):
        n_tables = len(self.schema)
        str_repr = TextStyle.BOLD + "MultiDataset Summary \n \n" + TextStyle.END

        # get the total number of tables in the DB schema
        str_repr += (
            TextStyle.BOLD
            + "Number of tables: "
            + TextStyle.END
            + f"{n_tables} \n \n"
        )

        # Calculate the summary of the information to be shown
        summary = []

        for table, table_details in self.schema.items():
            pk = table_details.primary_keys
            fk = [key.column for key in table_details.foreign_keys]

            table_summary = {"Table name": table,
                             "Num cols": len(table_details.columns),
                             "Num rows": self[table].nrows if self._datasets[table]
                             is not None else "Number of rows not yet computed",
                             "Primary keys": pk if len(pk) else '',
                             "Foreign keys": fk if len(fk) else '',
                             "Notes": ""}

            summary.append(table_summary)

        str_repr += DataFrame(summary).to_string()

        return str_repr

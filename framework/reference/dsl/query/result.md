Module superlinked.framework.dsl.query.result
=============================================

Classes
-------

`Result(schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject, entries: collections.abc.Sequence[superlinked.framework.dsl.query.result.ResultEntry], knn_params: collections.abc.Mapping[str, typing.Any] | None = None)`
:   A class representing the result of a query.
    
    Attributes:
        schema (IdSchemaObject): The schema of the result.
        entries (Sequence[ResultEntry]): A list of result entries.

    ### Class variables

    `entries: collections.abc.Sequence[superlinked.framework.dsl.query.result.ResultEntry]`
    :

    `knn_params: collections.abc.Mapping[str, typing.Any] | None`
    :

    `schema: superlinked.framework.common.schema.id_schema_object.IdSchemaObject`
    :

    ### Methods

    `to_pandas(self) ‑> pandas.core.frame.DataFrame`
    :   Converts the query result entries into a pandas DataFrame.
        
        Each row in the DataFrame corresponds to a single entity in the result, with
        columns representing the fields of the stored objects. An additional score column
        is present which shows similarity to the query vector.
        
        Returns:
            DataFrame: A pandas DataFrame where each row represents a result entity, and
                each column corresponds to the fields of the stored objects. Additionally,
                it contains the above-mentioned score column.

`ResultEntry(entity: superlinked.framework.common.storage_manager.search_result_item.SearchResultItem, stored_object: dict[str, typing.Any])`
:   Represents a single entry in a Result, encapsulating the entity and its associated data.
    
    Attributes:
        entity (SearchResultItem): The entity of the result entry.
            This is an instance of the SearchResultItem class, which represents a unique entity in the system.
            It contains header information such as the entity's ID and schema and the queried fields.
        stored_object (dict[str, Any]): The stored object of the result entry.
            This is essentially the raw data that was input into the system.

    ### Class variables

    `entity: superlinked.framework.common.storage_manager.search_result_item.SearchResultItem`
    :

    `stored_object: dict[str, typing.Any]`
    :
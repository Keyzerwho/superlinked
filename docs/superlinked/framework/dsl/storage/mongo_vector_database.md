Module superlinked.framework.dsl.storage.mongo_vector_database
==============================================================

Classes
-------

`MongoVectorDatabase(host: str, db_name: str, cluster_name: str, project_id: str, admin_api_user: str, admin_api_password: str, **extra_params: Any)`
:   MongoDB implementation of the VectorDatabase.
    
    This class provides a MongoDB-based vector database connector.
    
    Initialize the MongoVectorDatabase.
    
    Args:
        host (str): The hostname of the MongoDB server.
        db_name (str): The name of the database.
        cluster_name (str): The name of the MongoDB cluster.
        project_id (str): The project ID for MongoDB.
        admin_api_user (str): The admin API username.
        admin_api_password (str): The admin API password.
        **extra_params (Any): Additional parameters for the MongoDB connection.

    ### Ancestors (in MRO)

    * superlinked.framework.dsl.storage.vector_database.VectorDatabase
    * abc.ABC
    * typing.Generic
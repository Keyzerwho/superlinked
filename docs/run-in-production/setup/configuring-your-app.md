---
# description: >-
icon: square-sliders
---

# Server Configuration Guidelines

The application's main logic resides in the Superlinked configuration files. These are where you define your application's structure and behavior using the Superlinked library.

By default, all examples within this documentation utilize an in-memory database with a single worker. This configuration is optimal for testing and initial experimentation with the Superlinked framework. For detailed instructions on configuring and employing alternative vector databases, please refer to the [vector databases documentation.](../vdbs/vector_databases.md). For information on how to scale the server, read the [Scaling the Server with Concurrent Workers](#scaling-the-server-with-concurrent-workers) section.

To begin interacting with the system, you may start with the basic example application found [here](example/simple/api.py).
For a more complex yet approachable example, refer to the Amazon case study [here](example/amazon/api.py).

For advanced examples on constructing spaces and queries, please explore the [Superlinked notebooks](https://github.com/superlinked/superlinked/tree/main).

> Important Note: The `RecencySpace` feature is turned off by default due to the constraints of this release. For a detailed explanation and instructions on enabling it, refer to the [Using Recency Space](#using-recency-space) section of the documentation.

> Note: The primary aim of this document is to guide you on how to operate the Superlinked system with your preferred configuration, rather than explaining the inner workings of the Superlinked components. For a deeper understanding of the components, please refer to the notebooks mentioned above.

## Understanding the building blocks of the application

A functional application is structured around three core components:
- `index.py` - Defines schemas, spaces, and indexes
- `query.py` - Specifies the queries
- `api.py` - Configures the executor that integrates the aforementioned components and other crucial configurations

### index.py
```python
# linked-file:example/dummy/index.py
from superlinked.framework.common.schema.id_schema_object import IdField
from superlinked.framework.common.schema.schema import schema
from superlinked.framework.common.schema.schema_object import String
from superlinked.framework.dsl.index.index import Index
from superlinked.framework.dsl.space.text_similarity_space import TextSimilaritySpace


@schema
class YourSchema:
    id: IdField
    attribute: String


your_schema = YourSchema()

model_name = "<your model name goes here>"  # Ensure that you replace this with a valid model name!
text_space = TextSimilaritySpace(text=your_schema.attribute, model=model_name)

index = Index(text_space)
```

In this file, a schema is defined to structure your input data. Additionally, a space is specified, which must include at least one attribute from your schema, and an index is created to aggregate and integrate these spaces.

> It is crucial to understand that all definitions in this file determine the vectors of your elements. Any modifications to this file, such as adding a new space or altering the schema, will render the previously ingested data invalid, necessitating re-ingestion.

### query.py

```python
# linked-file:example/dummy/query.py
from superlinked.framework.dsl.query.param import Param
from superlinked.framework.dsl.query.query import Query

from .index import index, text_space, your_schema

query = (
    Query(index)
    .find(your_schema)
    .similar(
        text_space.text,
        Param("query_text"),
    )
)
```

In the `query.py` file, you should define your queries. These queries are designed to search within your data by configuring weights, limits, radius, and other critical parameters to optimize the retrieval of desired results.

### api.py

```python
# linked-file:example/dummy/api.py
from superlinked.framework.dsl.executor.rest.rest_configuration import RestQuery
from superlinked.framework.dsl.executor.rest.rest_descriptor import RestDescriptor
from superlinked.framework.dsl.executor.rest.rest_executor import RestExecutor
from superlinked.framework.dsl.registry.superlinked_registry import SuperlinkedRegistry
from superlinked.framework.dsl.source.rest_source import RestSource
from superlinked.framework.dsl.storage.in_memory_vector_database import InMemoryVectorDatabase

from .index import index, your_schema
from .query import query

your_source: RestSource = RestSource(your_schema)
your_query = RestQuery(RestDescriptor("query"), query)

executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[your_query],
    vector_database=InMemoryVectorDatabase(),
)

SuperlinkedRegistry.register(executor)
```

In this document, you set up your source, which acts as the entry point for your schema into the application. The `RestSource` can use a `RestDescriptor` to specify the path for adding data to your system. The `RestQuery` function wraps your query in a `RestDescriptor`, giving your query a name that makes it callable through the REST API. In the example shown, the path is set to `/api/v1/search/query`. Here, you assign a name to the last part of the path, assuming you stick with the default settings. [More detailed API info](#customize-your-api)

The executor acts as the heart of your application, needing all the necessary information to function. It requires your sources to bring in data, indices to understand the data structure, queries to help you search effectively, and finally, the vector database where all the data is stored.

This configuration eliminates the need for manual computation setup, enabling you to focus on defining the structure and behavior of your application. The Superlinked library manages the execution of your queries and the retrieval of results when the application is executed. This method also simplifies application updates, as it removes the necessity to SSH into the server for editing files directly.

You can find more detailed information and examples of various features in the [Superlinked feature notebooks](https://github.com/superlinked/superlinked/tree/main/notebook/feature). The [basic_building_blocks.ipynb](https://github.com/superlinked/superlinked/blob/main/notebook/feature/basic_building_blocks.ipynb) notebook provides a comprehensive guide on the basic structure and how to use it, while the other notebooks cover various features of the Superlinked library.

In this deployment setup, you are not required to define any computations as you would in the [basic_building_blocks.ipynb](https://github.com/superlinked/superlinked/blob/main/notebook/feature/basic_building_blocks.ipynb) notebook. Instead, your focus will be on defining the schema, the text similarity space, the index, the query, the REST source, and the executor.

## Configuring the data loader

The system has a feature to load data from file(s) either from local or remote.

> Note: In the absence of specified chunking, the loader will attempt to read and load the entire file into the system by default. Mind your memory! If possible, utilize file formats that support chunking and include the necessary parameters in the `pandas_read_kwargs` as indicated below.

Constraints: 
- When running your preview locally, only local files or public ones from remote sources can be used. Targeting an S3 bucket or GCP that requires authentication is not possible.
- When running in the cloud, for example on GCP, you can target private Google Cloud Storage (GCS) bucket but only those that the Google Cloud Engine (GCE) instance has access to. 
  It will utilize its own authentication and authorization, but no other private cloud sources like S3 can be used. Local files on the GCE or any public file that doesn't require authorization can also be used.

### Incorporate Data Source

Create a specific source that can point to a local or a remote file. This file can be parsed and loaded into the system more efficiently than invoking the REST endpoint for each piece of data:
```python
# The path can be a local file, a remote. The available DataFormats are: [JSON, CSV, PARQUET, ORC, XML, FWF]
# The `name_of_your_loader` is an optional parameter, which is the identifier of your loader. Read more about it below the code block.
# The last argument is a pass through argument that pandas should be able to use so use the format that is compatible with pandas.
# Note: the pandas_read_kwargs is an optional parameter, if you don't need any customization, it will use the defaults.
config = DataLoaderConfig("https://path-to-your-file.csv", DataFormat.CSV, "name_of_your_loader", pandas_read_kwargs={"sep": ";"})
data_loader_source = DataLoaderSource(your_schema, config) # Add your config to the source. This is mandatory.

executor = RestExecutor(
    sources=[your_source, data_loader_source], # Incorporate the data_loader_source into the sources here.
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
)
```

> Name of your data loader: The `name` parameter in `DataLoaderConfig` is optional. By default, it adopts the snake_case version of your schema's name used in `DataLoaderSource`. If you have multiple data loaders for the same schema or prefer a different name, simply set the `name` parameter accordingly.
> Note that the name will always be converted to snake_case. To see the configured data loaders in your system, refer to the [API documentation](interacting-with-app-via-api.md#see-available-data-loaders).

The data loader is now configured but **it only runs if you send a request to the data loader endpoint!** To see how to trigger it, check the API documentation [here](api.md#trigger-the-data-load)

## Optional steps

### Schema to column mappings

By default, the system will attempt to parse your file, hence the column names should align with your schema attributes. If an `id` column has a different name for example, as well as the other schema fields, it needs to be mapped to the schema you are attempting to load. To map field names to your schema, utilize the data parser as shown below:
```python
# Instantiate a DataFrameParser object, composed of the schema you wish to map and the actual mapping. The format for mapping is: `<schema.field>: <column_name>`
# Note: If the column names are exactly the same (case sensitive) as your schema, you don't need to provide a parser for the source at all.
data_frame_parser = DataFrameParser(your_schema, mapping={your_schema.id: "id_field_name", your_schema.attribute: "custom_field_name"})
data_loader_source = DataLoaderSource(your_schema, config, data_frame_parser) # Incorporate the parser into your source
```

### Data Chunking

Data chunking allows you to load more data than your memory could typically handle at once. This is particularly beneficial when dealing with data sets that span multiple gigabytes.
> If you're uncertain whether your data will fit into your memory, it's strongly advised to employ chunking to prevent unexpected problems. By setting the [log level to debug in the executor](../runner/executor/.env), you can view pandas memory information regardless of whether you're chunking the data. This assists in estimating memory usage.

To implement chunking, you'll need to use either CSV or JSON formats (specifically JSONL, which includes JSON objects on each line).

Here's an example of what a chunking configuration might look like:
```python
# For CSV
config = DataLoaderConfig("https://path-to-your-file.csv", DataFormat.CSV, pandas_read_kwargs={"chunksize": 10000})
# For JSON
config = DataLoaderConfig("https://path-to-your-file.jsonl", DataFormat.JSON, pandas_read_kwargs={"lines": True, "chunksize": 10000})
```

The Superlinked library performs internal batching for embeddings, with a default batch size of 10000. If you are utilizing a chunk size different from 10000, it is advisable to adjust this batch size to match your chunk size.
To modify this, alter the `ONLINE_PUT_CHUNK_SIZE` value [in this file](../runner/executor/.env)

### Customize your API

If you want to configure your API path, you can do that with the `RestEndpointConfiguration`, which can alter your URL. By default the API looks like:
- Query endpoint's path is: `/api/v1/search/<query_name>` which aligns with the schema: `/<api_root_path>/<query_path_prefix>/<query_name>` 
- Data ingestion endpoint's path is: `/api/v1/ingest/<schema_name>` which aligns with the schema: `/<api_root_path>/<ingest_path_prefix>/<schema_name>`
- The rest of the API is non configurable, that is part of the so called, management API.

To change the API's default path, see the following code, that let's you customize it:
```python
rest_endpoint_config = RestEndpointConfiguration(
    query_path_prefix="retrieve",
    ingest_path_prefix="insert",
    api_root_path="/superlinked/v3",
) # This will change the root path for both ingest and query endpoints

executor = RestExecutor(
    sources=[your_source],
    indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
    rest_endpoint_config=rest_endpoint_config # Incorporate your config here
)
```

### Using Recency Space

Recency Space has two current limitations:
- Recency embeddings become outdated over time as they are not recalculated periodically. Our encoder only needs a constant number of updates for this to work correctly, but that update mechanism has not been open-sourced yet - coming soon!
- At server startup, the application captures the server's current UTC timestamp as `now`. Each modification and restart of the application will result in a new timestamp, which does not dynamically update during runtime.

The first one is a known limitation that will be fixed in the near future. The second one can be solved with setting the timestamp to a fixed value.
```python
NOW = int(datetime(year=2024, month=1, day=2, tzinfo=UTC).timestamp()) # Here you can set the exact date to work with. Note: you can set hours, minute and so on.
EXECUTOR_DATA = {CONTEXT_COMMON: {CONTEXT_COMMON_NOW: NOW}} # Then use the following dict structure
```

Then add the `EXECUTOR_DATA` to your executor, like:

```python
executor = RestExecutor(
    sources=[source], indices=[index],
    queries=[RestQuery(RestDescriptor("query"), query)],
    vector_database=InMemoryVectorDatabase(),
    context_data=EXECUTOR_DATA, # Add your executor data here
)
```

Finally, you need to set a flag to prevent exceptions when utilizing Recency Space. Set the `DISABLE_RECENCY_SPACE` flag to `false` in the [.env config file](../runner/executor/.env)

### GPU acceleration

If your system's host machine is equipped with a GPU, this documentation provides guidance on leveraging it for computational tasks. GPU acceleration is available exclusively for text embedding processes and depends on explicit activation. It is most effective when processing large batches of data, specifically within the context of the data loading feature.

> Ensure that your system has a GPU compatible with PyTorch and that the GPU drivers are up to date. This documentation is specifically tailored for configurations running within Docker, not natively, due to Docker's limitation of only supporting NVidia GPUs as of now.

The following change will be needed in the `compose.yaml` file:
```dockerfile
version: "3"
services:
  poller:
    ...
  executor:
    depends_on:
      - poller
    build:
      context: runner
      dockerfile: executor/Dockerfile
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    ...
```

To activate GPU support in Superlinked, configure the `GPU_EMBEDDING_THRESHOLD` environment variable within the [.env](../runner/executor/.env) file for the executor service. Ensure that this value does not exceed the `ONLINE_PUT_CHUNK_SIZE` specified in the same configuration file. The appropriate threshold value is contingent upon the computational capabilities of the server's GPU and CPU; however, it is recommended to set a minimum threshold of 10000. This parameter determines the minimum size of data batches for which GPU acceleration is employed, thereby enhancing the performance of bulk embedding operations. A value of 0 indicates that GPU acceleration is disabled during the embedding process.

### Scaling the Server with Concurrent Workers

To enhance the server's throughput, it is feasible to deploy multiple worker processes. This can be configured by modifying the `WORKER_COUNT` parameter in the [compose.yaml](../compose.yaml) file, initially set to `WORKER_COUNT=1`. For optimal configuration, empirical benchmarking is recommended, though a heuristic approach suggests allocating one worker per virtual CPU.

> Important to note: When scaling to multiple workers, the utilization of an in-memory database becomes inaccessible. It is crucial to transition to a persistent vector database, as provided by the connectors available within the Superlinked ecosystem.
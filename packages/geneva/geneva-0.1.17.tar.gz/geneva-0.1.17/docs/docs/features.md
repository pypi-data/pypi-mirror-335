# Feature Engineering

## User Defined Functions

`Geneva` uses Python User Defined Functions (**UDFs**) to define features (columns) in a Lance dataset.

It uses Python type hints to infer the input and output
[arrow data types](https://arrow.apache.org/docs/python/api/datatypes.html).

### Scalar UDF

The simplest form is a scalar UDF, which processes one row at a time:

```python
from geneva import udf

@udf
def simple_udf(x: int, y: float) -> float:
    return x * y
```

### Batched UDF

For better performance, you can also define batch UDFs that process multiple rows at once using `pyarrow.RecordBatch`:

```python

import pyarrow as pa

from geneva import udf

@udf(data_type=pa.int32(), input_columns=["prompt"])
def batch_str_len(batch: pa.RecordBatch) -> pa.Array:
    return pa.compute.utf8_length(batch["prompt"])
```

!!! note

    It is required to specify `data_type` in the ``@udf`` decorator for batched **UDF**,
    which defines `pyarrow.DataType` of the returned `pyarrow.Array`.

    Optionally, user can specify `input_columns` to scan more efficiently,
    because [Lance is a columnar format](https://github.com/lancedb/lance).

For example, we can specify the data type of an embedding function:

```python

@udf(data_type=pa.list_(pa.float32(), 1536), input_columns=["prompt"])
def openai_embedding(batch: pa.RecordBatch) -> pa.Array:
    resp = self.client.embeddings.create(
        model=self.model, input=batch["prompt"].to_pylist())
    return pa.array(resp.data[0].embedding)
```

### Stateful UDF

One can also define a `Stateful` UDF that retains its state across each call.
It optimizes for initializing heavy resource on distributed workers.

A `Stateful` UDF is a `Callable` class, with `__call__()` method.

```python
from typing import Callable
from openai import OpenAI

@udf(data_type=pa.list_(pa.float32(), 1536))
class OpenAIEmbedding(Callable):
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        # Per-worker openai client
        self.client: OpenAI | None = None

    def __call__(self, text: str) -> pa.Array:
        if self.client is None:
            self.client = OpenAI()

        resp = self.client.embeddings.create(model=self.model, input=text)
        return pa.array(resp.data[0].embeddings)
```

??? note

    The state is guaranteed on each distributed Worker.

## UDF API

All UDFs are decorated by ``@geneva.udf``.

::: geneva.udf
    options:
      annotations_path: brief
      show_source: false


# Register a Virtual Column

!!! warning

    Unstable API.

With Python UDF, a virtual column (ML feature) can be registered via `Table.add_columns()`
method.

```python

import geneva

db = geneva.connect("db://my_video")

tbl = db.open_table("youtube-1000")
tbl.add_columns({"openai": OpenAIEmbedding()})
```

A distributed job will be triggered in the backend to run this **UDF**.

We currently support two backends: [Ray](https://www.anyscale.com/product/open-source/ray) or [Google Dataflow](https://cloud.google.com/products/dataflow):

The backend configuration specified via SDK:

=== "Ray"

    ```python
    import geneva
    import ray
    import pyarrow as pa
    from geneva import udf

    ray.init(address="ray://<ip-head-node>")

    @udf()
    def text_len(prompt: str) -> int:
        return len(prompt)

    db = geneva.connect("db://<my_db>")
    tbl = db.open_table("my_table")

    tbl.run({"text_len": text_len}, ["prompt"])
    ```

## Checkpoint

Each UDF execution is checkpointed: expensive intermediate results are stored so work is not lost during job failure and resumption.

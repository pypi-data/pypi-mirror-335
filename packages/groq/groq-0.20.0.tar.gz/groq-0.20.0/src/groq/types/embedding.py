# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Embedding"]


class Embedding(BaseModel):
    embedding: Union[List[float], str]
    """The embedding vector, which is a list of floats.

    The length of vector depends on the model as listed in the
    [embedding guide](/docs/guides/embeddings).
    """

    index: int
    """The index of the embedding in the list of embeddings."""

    object: Literal["embedding"]
    """The object type, which is always "embedding"."""

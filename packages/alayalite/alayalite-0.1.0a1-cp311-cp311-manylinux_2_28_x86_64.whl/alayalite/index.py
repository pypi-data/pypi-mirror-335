# Copyright 2025 AlayaDB.AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

import numpy as np

from ._alayalitepy import PyIndexInterface as _PyIndexInterface
from .common import (
    VectorLike,
    VectorLikeBatch,
    _assert,
)
from .schema import IndexParams, load_schema


class Index:
    """
    Initialize a new Index instance.

    Args:
        name (str): Name identifier for the index. Defaults to "default".
        params (IndexParams): Configuration parameters for the index.
    The Index class provides a Python interface for managing and querying vector indices.
    """

    def __init__(self, name: str = "default", params: IndexParams = IndexParams()):
        """
        Initialize a new Index instance.

        Args:
            name (str): Name identifier for the index. Defaults to "default".
            params (IndexParams): Configuration parameters for the index.
        """
        self.__name = name
        self.__params = params

        self.__index = None  # late initialization

        self.__is_initialized = False
        self.__dim = None  # It will be set when fitting the index

    def get_data_by_id(self, id: int) -> VectorLike:
        """
        Retrieve the vector data associated with a given ID.

        Args:
            id (int): The ID of the vector to retrieve.

        Returns:
            VectorLike: The corresponding vector data.
        """
        return self.__index.get_data_by_id(id)

    def fit(
        self,
        vectors: VectorLikeBatch,
        ef_construction: int = 100,
        num_threads: int = 1,
    ):
        """
        Build the index with the given set of vectors.

        Args:
            vectors (VectorLikeBatch): A 2D array of vectors to construct the index.
            ef_construction (int): Controls the accuracy of index construction. Default is 100.
            num_threads (int): Number of threads to use during index construction. Default is 1.
        """
        if self.__is_initialized:
            raise RuntimeError("An index can be only fitted once")

        _assert(vectors.ndim == 2, "vectors must be a 2D array")
        data_type = np.array(vectors).dtype
        print(data_type)
        if self.__params.data_type is None:
            self.__params.data_type = data_type
        elif self.__params.data_type != np.array(vectors).dtype:
            raise ValueError(f"Data type mismatch: {self.__params.data_type} vs {data_type}")
        self.__params.fill_none_values()
        self.__dim = vectors.shape[1]
        self.__index = _PyIndexInterface(self.__params.to_cpp_params())
        self.__is_initialized = True

        print(
            f"fitting index with the following parameters: \n"
            f"  vectors.shape: {vectors.shape}, num_threads: {num_threads}, ef_construction: {ef_construction}\n"
            f"start fitting index..."
        )
        self.__index.fit(vectors, ef_construction, num_threads)

    def insert(self, vectors: VectorLike, ef: int = 100):
        """
        Insert a new vector into the index.

        Args:
            vectors (VectorLike): A 1D vector to be inserted.
            ef (int): Search parameter controlling retrieval accuracy. Default is 100.

        Returns:
            int: The assigned ID of the inserted vector.
        """
        _assert(self.__index is not None, "Index is not init yet")
        _assert(vectors.ndim == 1, "vectors must be a 1D array")
        _assert(
            vectors.shape[0] == self.__dim,
            f"vectors dimension must match the dimension of the vectors used to fit the index."
            f"fit data dimension: {self.__dim}, vectors dimension: {vectors.shape[0]}",
        )
        ret = self.__index.insert(vectors, ef)
        if (
            (self.__params.id_type == np.uint32 and ret == 4294967295)
            or (self.__params.id_type == np.uint64 and ret == 18446744073709551615)
            or ret == -1
        ):
            raise RuntimeError("The index is full, cannot insert more vectors")
        return ret

    def remove(self, id: int) -> None:
        """
        Remove a vector from the index by ID.

        Args:
            id (int): The ID of the vector to remove.
        """
        _assert(self.__index is not None, "Index is not init yet")
        self.__index.remove(id)

    def search(self, query: VectorLike, topk: int, ef_search: int = 100) -> VectorLike:
        """
        Perform a nearest neighbor search for a given query vector.

        Args:
            query (VectorLike): A 1D query vector.
            topk (int): Number of nearest neighbors to retrieve.
            ef_search (int): Search accuracy parameter. Default is 100.

        Returns:
            VectorLike: The top-k nearest neighbors.
        """
        _assert(self.__index is not None, "Index is not init yet")
        _assert(query.ndim == 1, "query must be a 1D array")
        _assert(
            query.shape[0] == self.__dim,
            f"query dimension must match the dimension of the vectors used to fit the index."
            f"fit data dimension: {self.__dim}, query dimension: {query.shape[0]}",
        )

        return self.__index.search(query, topk, ef_search)

    def batch_search(
        self,
        queries: VectorLikeBatch,
        topk: int,
        ef_search: int = 100,
        num_threads: int = 1,
    ) -> VectorLikeBatch:
        """
        Perform a batch search for multiple query vectors.

        Args:
            queries (VectorLikeBatch): A 2D array of query vectors.
            topk (int): Number of nearest neighbors to retrieve per query.
            ef_search (int): Search accuracy parameter. Default is 100.
            num_threads (int): Number of threads to use for searching. Default is 1.

        Returns:
            VectorLikeBatch: The top-k nearest neighbors for each query.
        """
        _assert(self.__index is not None, "Index is not init yet")
        _assert(queries.ndim == 2, "queries must be a 2D array")
        _assert(
            queries.shape[1] == self.__dim,
            f"query dimension must match the dimension of the vectors used to fit the index."
            f"fit data dimension: {self.__dim}, query dimension: {queries.shape[1]}",
        )

        return self.__index.batch_search(queries, topk, ef_search, num_threads)

    def get_dim(self):
        """
        Get the dimensionality of vectors stored in the index.

        Returns:
            int: The dimension of the indexed vectors.
        """
        return self.__dim

    def save(self, url) -> dict:
        """
        Save the index to a specified directory.

        Args:
            url (str): Path where the index should be saved.

        Returns:
            dict: Metadata describing the saved index.
        """
        if not os.path.exists(url):
            os.makedirs(url)

        index_path = self.__params.index_path(url)
        data_path = self.__params.data_path(url)
        quant_path = self.__params.quant_path(url)

        self.__index.save(index_path, data_path, quant_path)
        return {"type": "index", "index": self.__params.to_json_dict()}

    @classmethod
    def load(cls, url, name):
        """
        Load an existing index from disk.

        Args:
            url (str): Directory where the index is stored.
            name (str): Name of the index.

        Returns:
            Index: The loaded index instance.
        """
        index_url = os.path.join(url, name)

        if not os.path.exists(index_url):
            raise RuntimeError("The index file does not exist")

        schema_url = os.path.join(index_url, "schema.json")
        params = IndexParams.from_str_dict(load_schema(schema_url)["index"])
        instance = cls(name, params)
        instance.__index = _PyIndexInterface(params.to_cpp_params())

        index_path = params.index_path(index_url)
        data_path = params.data_path(index_url)
        quant_path = params.quant_path(index_url)

        instance.__index.load(index_path, data_path, quant_path)
        instance.__is_initialized = True
        instance.__dim = instance.__index.get_data_dim()
        return instance

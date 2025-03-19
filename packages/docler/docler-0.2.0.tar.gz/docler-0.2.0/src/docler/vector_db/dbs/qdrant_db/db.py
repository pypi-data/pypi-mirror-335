"""Qdrant vector store backend implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar
import uuid

from docler.vector_db.base import SearchResult, VectorStoreBackend


if TYPE_CHECKING:
    import numpy as np


logger = logging.getLogger(__name__)


class QdrantBackend(VectorStoreBackend):
    """Qdrant implementation of vector store backend."""

    REQUIRED_PACKAGES: ClassVar = {"qdrant-client"}

    def __init__(
        self,
        collection_name: str = "default",
        location: str | None = None,
        url: str | None = None,
        api_key: str | None = None,
        vector_size: int = 1536,
        prefer_grpc: bool = True,
    ):
        """Initialize Qdrant backend.

        Args:
            collection_name: Name of collection to use
            location: Path to local storage (memory if None)
            url: URL of Qdrant server (overrides location)
            api_key: API key for Qdrant cloud
            vector_size: Size of vectors to store
            prefer_grpc: Whether to prefer gRPC over HTTP
        """
        import qdrant_client
        from qdrant_client.http import models

        # Create client based on configuration
        client_kwargs: dict[str, Any] = {"prefer_grpc": prefer_grpc}
        if url:
            client_kwargs["url"] = url
            if api_key:
                client_kwargs["api_key"] = api_key
        elif location:
            client_kwargs["location"] = location
        else:
            client_kwargs["location"] = ":memory:"

        self._client = qdrant_client.QdrantClient(**client_kwargs)
        self._collection_name = collection_name

        # Check if collection exists
        collections = self._client.get_collections().collections
        collection_names = [c.name for c in collections]

        # Create collection if it doesn't exist
        if self._collection_name not in collection_names:
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE
                ),
            )

    async def add_vector(
        self,
        vector: np.ndarray,
        metadata: dict[str, Any],
        id_: str | None = None,
    ) -> str:
        """Add single vector to Qdrant.

        Args:
            vector: Vector embedding to store
            metadata: Metadata dictionary
            id_: Optional ID (generated if not provided)

        Returns:
            ID of the stored vector
        """
        import anyenv
        from qdrant_client.http import models

        # Generate ID if not provided
        if id_ is None:
            id_ = str(uuid.uuid4())

        # Convert numpy array to float and then list
        vector_list = vector.astype(float).tolist()

        point = models.PointStruct(
            id=id_,
            vector=vector_list,
            payload=metadata,
        )

        await anyenv.run_in_thread(
            self._client.upsert,
            collection_name=self._collection_name,
            points=[point],
        )

        return id_

    async def add_vectors(
        self,
        vectors: list[np.ndarray],
        metadata: list[dict[str, Any]],
        ids: list[str] | None = None,
    ) -> list[str]:
        """Add vectors to Qdrant.

        Args:
            vectors: List of vector embeddings
            metadata: List of metadata dictionaries
            ids: Optional list of IDs

        Returns:
            List of IDs for stored vectors
        """
        import anyenv
        from qdrant_client.http import models

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in vectors]

        # Convert numpy arrays to lists and create points
        points = []
        for i, vector in enumerate(vectors):
            # Convert to float64 then to list to ensure compatibility
            vector_list = vector.astype(float).tolist()

            points.append(
                models.PointStruct(id=ids[i], vector=vector_list, payload=metadata[i])
            )

        # Upsert vectors
        await anyenv.run_in_thread(
            self._client.upsert, collection_name=self._collection_name, points=points
        )

        return ids

    async def get_vector(
        self,
        chunk_id: str,
    ) -> tuple[np.ndarray, dict[str, Any]] | None:
        """Get a vector and its metadata by ID.

        Args:
            chunk_id: ID of vector to retrieve

        Returns:
            Tuple of (vector, metadata) if found, None if not
        """
        import anyenv
        import numpy as np

        points = await anyenv.run_in_thread(
            self._client.retrieve,
            collection_name=self._collection_name,
            ids=[chunk_id],
            with_payload=True,
            with_vectors=True,
        )

        if not points:
            return None

        point = points[0]
        return np.array(point.vector), point.payload

    async def update_vector(
        self,
        chunk_id: str,
        vector: np.ndarray | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update an existing vector.

        Args:
            chunk_id: ID of vector to update
            vector: New vector embedding (unchanged if None)
            metadata: New metadata (unchanged if None)

        Returns:
            True if vector was updated, False if not found
        """
        import anyenv
        from qdrant_client.http import models

        # Get current vector if we need it
        current = None
        if vector is None or metadata is None:
            current = await self.get_vector(chunk_id)
            if current is None:
                return False

        # Use new values or keep current ones
        current_vector, current_metadata = current if current else (None, {})
        final_vector = vector if vector is not None else current_vector
        final_metadata = metadata if metadata is not None else current_metadata
        assert final_vector
        # Create point for update
        point = models.PointStruct(
            id=chunk_id,
            vector=final_vector.astype(float).tolist(),
            payload=final_metadata,
        )

        try:
            await anyenv.run_in_thread(
                self._client.upsert,
                collection_name=self._collection_name,
                points=[point],
            )
        except Exception:  # noqa: BLE001
            return False
        else:
            return True

    async def delete(self, chunk_id: str) -> bool:
        """Delete vector by ID.

        Args:
            chunk_id: ID of vector to delete

        Returns:
            True if vector was deleted, False if not found
        """
        import anyenv
        from qdrant_client.http import models
        from qdrant_client.http.exceptions import UnexpectedResponse

        try:
            # Create selector for the point ID
            selector = models.PointIdsList(points=[chunk_id])

            # Delete the point
            await anyenv.run_in_thread(
                self._client.delete,
                collection_name=self._collection_name,
                points_selector=selector,
            )
        except UnexpectedResponse:
            # If point not found or other error
            return False
        except Exception:  # noqa: BLE001
            # Any other exception
            return False
        else:
            return True

    async def search_vectors(
        self,
        query_vector: np.ndarray,
        k: int = 4,
        filters: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search Qdrant for similar vectors.

        Args:
            query_vector: Vector to search for
            k: Number of results to return
            filters: Optional filters to apply

        Returns:
            List of search results
        """
        import anyenv
        from qdrant_client.http import models

        # Convert numpy to list
        vector_list = query_vector.astype(float).tolist()

        # Build filter if needed
        filter_query = None
        if filters:
            conditions = []
            for field_name, value in filters.items():
                if isinstance(value, list):
                    # Handle list values
                    conditions.append(
                        models.FieldCondition(
                            key=field_name,
                            match=models.MatchAny(any=value),
                        )
                    )
                else:
                    # Handle single values
                    conditions.append(
                        models.FieldCondition(
                            key=field_name,
                            match=models.MatchValue(value=value),
                        )
                    )

            if conditions:
                filter_query = models.Filter(must=conditions)

        # Execute search
        results = await anyenv.run_in_thread(
            self._client.search,
            collection_name=self._collection_name,
            query_vector=vector_list,
            limit=k,
            with_payload=True,
            filter=filter_query,
        )

        # Format results
        search_results = []
        for hit in results:
            payload = hit.payload or {}
            text = payload.pop("text", None) if payload else None

            result = SearchResult(
                chunk_id=str(hit.id),
                score=hit.score,
                metadata=payload,
                text=str(text) if text is not None else None,
            )
            search_results.append(result)

        return search_results

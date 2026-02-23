"""Vector memory service — S3 + faiss-cpu for semantic search.

Stores memory facts as JSON files in S3. On search, loads recent memories
into a faiss-cpu IndexFlatIP for cosine similarity search.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

import boto3


class MemoryService:
    """Manages vector memory in S3 with faiss-cpu for search."""

    def __init__(self):
        self._bucket = os.getenv("MEMORY_BUCKET", "")
        self._s3 = boto3.client("s3") if self._bucket else None

    def search(
        self, user_id: str, query: str, top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Cosine similarity search over user's memories using faiss-cpu."""
        if not self._s3 or not self._bucket:
            return []

        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return []

            # Load all memory files for this user
            memories = self._load_user_memories(user_id)
            if not memories:
                return []

            # Filter to memories that have embeddings
            with_embeddings = [m for m in memories if m.get("embedding")]
            if not with_embeddings:
                return []

            # Build faiss index and search
            import numpy as np
            try:
                import faiss
            except ImportError:
                # faiss not available — fall back to numpy dot product
                return self._numpy_search(
                    query_embedding, with_embeddings, top_k
                )

            dim = len(query_embedding)
            index = faiss.IndexFlatIP(dim)  # inner product = cosine on normalized vectors

            # Stack all embeddings into a matrix
            vectors = np.array(
                [m["embedding"] for m in with_embeddings], dtype=np.float32
            )
            # Normalize for cosine similarity
            faiss.normalize_L2(vectors)
            index.add(vectors)

            # Normalize query vector
            q = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(q)

            k = min(top_k, len(with_embeddings))
            scores, indices = index.search(q, k)

            results = []
            for i, idx in enumerate(indices[0]):
                if idx < 0:
                    continue
                mem = with_embeddings[idx]
                results.append({
                    "id": mem.get("id", ""),
                    "userId": user_id,
                    "content": mem.get("content", ""),
                    "metadata": mem.get("metadata"),
                    "createdAt": mem.get("createdAt"),
                    "score": float(scores[0][i]),
                })
            return results

        except Exception:
            return []

    def _numpy_search(
        self,
        query_embedding: list[float],
        memories: list[dict],
        top_k: int,
    ) -> list[dict]:
        """Fallback search using numpy dot product when faiss unavailable."""
        import numpy as np

        q = np.array(query_embedding, dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-9)

        scored = []
        for mem in memories:
            v = np.array(mem["embedding"], dtype=np.float32)
            v = v / (np.linalg.norm(v) + 1e-9)
            score = float(np.dot(q, v))
            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            {
                "id": mem.get("id", ""),
                "userId": mem.get("userId", ""),
                "content": mem.get("content", ""),
                "metadata": mem.get("metadata"),
                "createdAt": mem.get("createdAt"),
                "score": score,
            }
            for score, mem in scored[:top_k]
        ]

    def extract_and_store(self, user_id: str, conversation_turn: str) -> None:
        """Extract key facts from a conversation turn and store in S3."""
        if not self._s3 or not self._bucket:
            return

        embedding = self._generate_embedding(conversation_turn)
        if not embedding:
            return

        memory_id = str(uuid.uuid4())
        doc = {
            "id": memory_id,
            "userId": user_id,
            "content": conversation_turn,
            "embedding": embedding,
            "metadata": {},
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }

        try:
            key = f"memories/{user_id}/{memory_id}.json"
            self._s3.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=json.dumps(doc),
                ContentType="application/json",
            )
        except Exception:
            pass

    def list_memories(self, user_id: str) -> list[dict]:
        """Return all memory entries for a user (without embeddings)."""
        if not self._s3 or not self._bucket:
            return []

        memories = self._load_user_memories(user_id)
        # Strip embeddings from response (they're large)
        for m in memories:
            m.pop("embedding", None)
        return memories

    def delete(self, user_id: str, memory_id: str) -> None:
        """Remove a specific memory file from S3."""
        if not self._s3 or not self._bucket:
            return
        try:
            key = f"memories/{user_id}/{memory_id}.json"
            self._s3.delete_object(Bucket=self._bucket, Key=key)
        except Exception:
            pass

    def _load_user_memories(self, user_id: str) -> list[dict]:
        """Load all memory JSON files for a user from S3."""
        if not self._s3 or not self._bucket:
            return []

        memories = []
        prefix = f"memories/{user_id}/"
        try:
            paginator = self._s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    try:
                        resp = self._s3.get_object(
                            Bucket=self._bucket, Key=obj["Key"]
                        )
                        doc = json.loads(resp["Body"].read())
                        memories.append(doc)
                    except Exception:
                        continue
        except Exception:
            pass
        return memories

    def _generate_embedding(self, text: str) -> list[float] | None:
        """Generate a 768-d embedding via Gemini embedding model."""
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        try:
            import httpx

            resp = httpx.post(
                "https://generativelanguage.googleapis.com/v1beta/models/"
                "text-embedding-004:embedContent",
                params={"key": api_key},
                json={"content": {"parts": [{"text": text}]}},
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json()["embedding"]["values"]
        except Exception:
            return None

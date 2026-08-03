# Retrieval Pipeline

## Retrieval Methods

### Dense Retrieval
- Uses embedding similarity (cosine distance)
- Finds semantically similar chunks
- Good for conceptual/meaning-based queries

### BM25 Retrieval
- Term frequency-based sparse retrieval
- Good for exact keyword matches
- Independent of embeddings

### Hybrid Retrieval
Combines dense and sparse retrieval:
```
score = (dense_weight * dense_score) + (bm25_weight * bm25_score)
```

Default weights: 0.6 dense, 0.4 BM25

## Reranking

Cross-encoder reranking improves relevance:
- Takes top-k results from hybrid retrieval
- Re-scores query-document pairs
- Returns top-rerank-k most relevant results

## Metadata Filtering

Filters can be applied at any stage:
- Workspace isolation (always applied)
- Dataset filtering
- Document type filtering
- Custom metadata filters

## Pipeline Flow

```
Query
  │
  ▼
[Embedding Generation]
  │
  ▼
[Vector Search] ──┐
  │               │
  ▼               │
[BM25 Search] ───┘
  │
  ▼
[Hybrid Merge]
  │
  ▼
[Metadata Filtering]
  │
  ▼
[Cross-Encoder Reranking]
  │
  ▼
Top-K Results
```

## Configuration

```yaml
retrieval:
  dense_weight: 0.6
  bm25_weight: 0.4
  top_k: 10
  rerank_top_k: 5
  similarity_threshold: 0.7
```

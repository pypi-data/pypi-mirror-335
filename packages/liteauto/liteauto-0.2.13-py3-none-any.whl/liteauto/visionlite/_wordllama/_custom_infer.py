import timeit
from typing import List, Tuple

import numpy as np
from wordllama import WordLlama



class WordLLamaCustomInfer:
    def __init__(self, wllm=None):
        self.wllm = wllm or WordLlama.load()

    def rank(
        self,
        query: str, docs: List[str], sort: bool = True, batch_size: int = 64
    ) -> List[Tuple[int, str, float]]:
        assert isinstance(query, str), "Query must be a string"
        query_embedding = self.wllm.embed(query)
        doc_embeddings = self.wllm.embed(docs, batch_size=batch_size)
        scores = self.wllm.vector_similarity(query_embedding[0], doc_embeddings)

        scores = np.atleast_1d(scores.squeeze())
        idx = np.arange(len(docs)).tolist()
        similarities = list(zip(idx, docs, scores.tolist()))
        if sort:
            similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def topk(
        self,
        query: str, candidates: List[str], k: int = 3) -> List[Tuple[int, str, float]]:
        ranked_docs = self.rank(query, candidates)
        return ranked_docs[:k]

    def auto_expanded_chunks(self,text,query,k=3):
        if not text:
            return None
        splits = self.wllm.split(text)
        ans = self.topk(query, splits, k=k)  # ( idx, text,score)
        ans_idx_sorted = sorted(ans, key=lambda x: x[0])
        window_sizes_per_idx = self.get_np_weights(len(ans_idx_sorted))
        points = [(aidx[0] - wsz, aidx[0] + wsz) for aidx, wsz in zip(ans_idx_sorted, window_sizes_per_idx)]
        filtered_points = self.merge_intervals(points)
        merged_text = ["".join(splits[p[0]:p[1] + 1]) for p in filtered_points]
        return merged_text


    def get_np_weights(self,size):
        weighted_sizes = np.arange(size, 0, -1)
        weighted_sizes = weighted_sizes / weighted_sizes.mean()
        weighted_list = (weighted_sizes + 1).astype(int)
        return weighted_list.tolist()


    def merge_intervals(self,intervals):
        # Handle empty or single interval case
        if not intervals:
            return []
        if len(intervals) == 1:
            return intervals

        # Sort intervals by start time
        intervals.sort(key=lambda x: x[0])

        merged = [intervals[0]]

        for current in intervals[1:]:
            previous = merged[-1]

            # If current interval overlaps with previous
            if current[0] <= previous[1]:
                # Update the end point of previous interval if needed
                merged[-1] = (previous[0], max(previous[1], current[1]))
            else:
                # Add non-overlapping interval to result
                merged.append(current)

        return merged
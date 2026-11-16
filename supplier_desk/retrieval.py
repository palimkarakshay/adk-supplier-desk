"""Small BM25 retriever over the policy fixture. No external dependencies."""
import math
import re

from .data import POLICY

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class BM25:
    def __init__(self, docs: list[dict], k1: float = 1.5, b: float = 0.75):
        self.docs = docs
        self.k1, self.b = k1, b
        self.toks = [tokenize(d["title"] + " " + d["text"]) for d in docs]
        self.avgdl = sum(len(t) for t in self.toks) / len(self.toks)
        df: dict[str, int] = {}
        for toks in self.toks:
            for term in set(toks):
                df[term] = df.get(term, 0) + 1
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, k: int = 2) -> list[dict]:
        scores = []
        for doc, toks in zip(self.docs, self.toks):
            score = 0.0
            for term in tokenize(query):
                tf = toks.count(term)
                if not tf:
                    continue
                norm = tf + self.k1 * (1 - self.b + self.b * len(toks) / self.avgdl)
                score += self.idf.get(term, 0.0) * tf * (self.k1 + 1) / norm
            scores.append((score, doc))
        scores.sort(key=lambda s: -s[0])
        return [{**d, "score": round(s, 3)} for s, d in scores[:k] if s > 0]


POLICY_INDEX = BM25(POLICY)

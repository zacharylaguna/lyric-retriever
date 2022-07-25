import re
import math

from collections import Counter
from stopwords import STOPWORDS


class Query:
    def __init__(self, _query):
        self.query = _query
        self.query_words = re.sub(r"[^a-zA-Z0-9_ ]", "", _query).split(" ")
        self.query_words = [
            query_word.lower()
            for query_word in self.query_words
            if query_word.lower() not in STOPWORDS
        ]


class BM25:
    """
    Okapi BM25

    Reference: http://ethen8181.github.io/machine-learning/search/bm25_intro.html

    Parameters
    ----------
    k1 : float, default 1.5
    b : float, default 0.75

    Attributes
    ----------
    tfs : list[dict{str: int}]
        Term Frequencies per document.

    dfs : dict[str, int]
        Document Frequencies per term.
        The number of documents that contain the term.

    idf : dict[str, int]
        Inverse Document Frequencies per term.

    doc_lens : list[int]
        Length of document (# terms).

    n_docs : int
        Number of documents in corpus.

    avg_doc_len : float
        Average length of documents (# terms) in corpus.
    """

    def __init__(self, _k1=1.5, _b=0.75):
        self.k1 = _k1
        self.b = _b

        self.tfs = []
        self.dfs = {}
        self.idf = {}
        self.doc_lens = []
        self.n_docs = 0
        self.avg_doc_len = 0

    def fit(self, _corpus):
        """
        Fit BM25 parameters using the given Corpus _corpus

        Args:
            _corpus (List[List[str]]): Each element of the list is a document
                                    and each document is a list of its terms

        Returns:
            self
        """

        tfs = []
        dfs = {}
        idf = {}
        doc_lens = []
        n_docs = 0

        for doc in _corpus:
            n_docs += 1
            doc_lens.append(len(doc))

            # Compute tf (term frequencies) of current doc
            tfs.append(Counter(doc))

            # Compute df (doc frequencies) of terms in current doc
            for term in doc:
                dfs[term] = dfs.get(term, 0) + 1

        # Compute the idf for a given term
        idf = {
            term: math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))
            for term, freq in dfs.items()
        }

        self.tfs = tfs
        self.dfs = dfs
        self.idf = idf
        self.doc_lens = doc_lens
        self.n_docs = n_docs
        self.avg_doc_len = sum(self.doc_lens) / self.n_docs

        return self

    def query(self, _query):
        """
        Rank documents in corpus based on given Query _query

        Args:
            _query (Query): Query object

        Returns:
            List[int]: List of sorted document indexes that
                    correspond to its relative rank for the given query
        """

        scores = [(i, self._score(_query, i)) for i in range(self.n_docs)]
        scores.sort(key=lambda score: score[1], reverse=True)

        return [score[0] for score in scores]

    def query_n(self, _query, _n=5):
        """
        Rank documents in corpus based on given Query _query
        Returns only the top _n documents

        Args:
            _query (Query): Query object
            _n (int, optional): Top _n documents will be returned. Defaults to 5.

        Returns:
            List[int]: List of _n sorted document indexes that
                    correspond to its relative rank for the given query
        """

        return self.query(_query)[:_n]

    def _score(self, _query, _index):
        score = 0.0

        dl = self.doc_lens[_index]  # Length of document at _index
        tf = self.tfs[_index]  # Term frequencies dictionary of document at _index

        for term in _query.query_words:
            if term not in tf:
                continue

            freq = tf[term]
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (
                1 - self.b + self.b * (dl / self.avg_doc_len)
            )

            score += self.idf[term] * (numerator / denominator)

        return score

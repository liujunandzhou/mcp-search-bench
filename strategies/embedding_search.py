"""
方案三：Embedding 语义检索
离线将所有工具描述向量化，在线用自然语言 query 做相似度检索。
使用 TF-IDF + 余弦相似度模拟 embedding 行为（无需外部向量模型依赖）。
"""

import re
import math
from collections import Counter
from data.tools_registry import get_all_tools, ToolDefinition, CATEGORY_META
from strategies.base import SearchStrategy, SearchResult
from utils.token_counter import count_tool_tokens, count_tokens, estimate_meta_tool_tokens

try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


# Embedding 方案暴露的元工具
EMBEDDING_META_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_tools",
            "description": "语义搜索飞书 API 工具。输入自然语言描述，返回最相关的工具列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "自然语言搜索查询"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量，默认 5",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def _tokenize(text: str) -> list[str]:
    """中英文混合分词"""
    tokens = []
    if HAS_JIEBA:
        tokens.extend(jieba.cut(text))
    else:
        # 简易分词：按标点和空格分割，中文逐字
        for part in re.split(r'[\s,./\-_:;()\[\]{}]+', text):
            # 英文单词
            en_words = re.findall(r'[a-zA-Z]+', part)
            tokens.extend(w.lower() for w in en_words)
            # 中文逐字/双字
            cn_chars = re.findall(r'[\u4e00-\u9fff]+', part)
            for seg in cn_chars:
                for i in range(len(seg)):
                    tokens.append(seg[i])
                    if i + 1 < len(seg):
                        tokens.append(seg[i:i+2])
    return [t.strip() for t in tokens if t.strip() and len(t.strip()) > 0]


class EmbeddingSearchStrategy(SearchStrategy):
    """Embedding 语义检索"""

    def __init__(self, min_score: float = 0.05):
        self._all_tools = get_all_tools()
        self._min_score = min_score
        self._build_index()

    def _build_index(self):
        """构建 TF-IDF 向量索引"""
        self._tool_texts = []
        for tool in self._all_tools:
            # 构建丰富的文本表示
            meta = CATEGORY_META.get(tool.category, {})
            text_parts = [
                tool.description,
                tool.description_en,
                tool.tool_id.replace(".", " "),
                tool.category,
                tool.sub_category,
                tool.operation,
                meta.get("name", ""),
                meta.get("description", ""),
                " ".join(meta.get("keywords", [])),
                " ".join(tool.tags),
            ]
            if tool.params:
                text_parts.append(tool.param_summary)
            self._tool_texts.append(" ".join(text_parts))

        if HAS_SKLEARN:
            if HAS_JIEBA:
                self._vectorizer = TfidfVectorizer(
                    tokenizer=_tokenize,
                    token_pattern=None,
                    max_features=5000,
                )
            else:
                self._vectorizer = TfidfVectorizer(
                    tokenizer=_tokenize,
                    token_pattern=None,
                    max_features=5000,
                )
            self._tfidf_matrix = self._vectorizer.fit_transform(self._tool_texts)
        else:
            # 回退到简单 TF-IDF 实现
            self._simple_index = []
            all_tokens = []
            for text in self._tool_texts:
                tokens = _tokenize(text)
                self._simple_index.append(Counter(tokens))
                all_tokens.extend(tokens)
            self._idf = {}
            total_docs = len(self._tool_texts)
            token_doc_count = Counter()
            for idx in self._simple_index:
                for token in idx:
                    token_doc_count[token] += 1
            for token, count in token_doc_count.items():
                self._idf[token] = math.log(total_docs / (1 + count))

    def _search_sklearn(self, query: str, top_k: int) -> list[tuple[int, float]]:
        """使用 sklearn TF-IDF 搜索"""
        query_vec = self._vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self._tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_k]
        return [(int(i), float(similarities[i])) for i in top_indices if similarities[i] > self._min_score]

    def _search_simple(self, query: str, top_k: int) -> list[tuple[int, float]]:
        """简单 TF-IDF 搜索（无 sklearn 依赖）"""
        query_tokens = Counter(_tokenize(query))

        # 计算查询的 TF-IDF 向量
        query_vec = {}
        for token, count in query_tokens.items():
            if token in self._idf:
                query_vec[token] = count * self._idf[token]

        if not query_vec:
            return []

        # 计算余弦相似度
        query_norm = math.sqrt(sum(v ** 2 for v in query_vec.values()))
        if query_norm == 0:
            return []

        scores = []
        for i, doc_tf in enumerate(self._simple_index):
            dot_product = 0
            doc_norm_sq = 0
            for token, count in doc_tf.items():
                tfidf = count * self._idf.get(token, 0)
                doc_norm_sq += tfidf ** 2
                if token in query_vec:
                    dot_product += query_vec[token] * tfidf

            doc_norm = math.sqrt(doc_norm_sq) if doc_norm_sq > 0 else 0
            if doc_norm > 0:
                sim = dot_product / (query_norm * doc_norm)
                if sim > self._min_score:
                    scores.append((i, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    @property
    def name(self) -> str:
        return "embedding"

    @property
    def name_cn(self) -> str:
        return "Embedding 语义检索"

    @property
    def description(self) -> str:
        return "工具描述向量化，相似度召回。通用性高，处理中文模糊意图效果好。"

    def search(self, query: str, top_k: int = 10) -> SearchResult:
        # 语义搜索
        if HAS_SKLEARN:
            results = self._search_sklearn(query, top_k)
        else:
            results = self._search_simple(query, top_k)

        result_tools = [self._all_tools[i] for i, _ in results]
        tool_ids = [t.tool_id for t in result_tools]

        # Token 消耗
        meta_tokens = estimate_meta_tool_tokens(EMBEDDING_META_TOOLS)
        # 返回结果的 token（Server 侧实现，只传匹配结果摘要）
        result_text = "\n".join(
            f"{t.tool_id}: {t.description}" for t in result_tools
        )
        result_tokens = count_tokens(result_text)

        failure_mode = ""
        if not results:
            failure_mode = "no_semantic_match"
        elif results[0][1] < 0.1:
            failure_mode = "low_confidence_match"

        return SearchResult(
            tool_ids=tool_ids,
            tool_definitions=result_tools,
            token_cost=meta_tokens + result_tokens,
            search_rounds=1,
            meta_tool_tokens=meta_tokens,
            result_tokens=result_tokens,
            failure_mode=failure_mode,
            details={
                "top_scores": [(self._all_tools[i].tool_id, round(s, 4)) for i, s in results[:5]],
                "backend": "sklearn" if HAS_SKLEARN else "simple",
            }
        )

    def get_initial_token_cost(self) -> int:
        return estimate_meta_tool_tokens(EMBEDDING_META_TOOLS)

import jieba
import re
from typing import List, Dict, Tuple, Set, Optional, Union
from datasketch import MinHash, MinHashLSH


class TextMatcher:
    def __init__(
            self,
            threshold: float = 0.5,
            num_perm: int = 128,
            is_raw_texts=True,
            stopwords_path: Optional[str] = None,
            user_dict_path: Optional[str] = None,

    ):
        """
        初始化文本匹配器

        Args:
            threshold: LSH 相似度阈值
            num_perm: MinHash 排列数
            stopwords_path: 停用词文件路径
            user_dict_path: 用户自定义词典路径
        """
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        # self.minhashes: Dict[str, MinHash] = {}
        self.raw_texts: Dict[str, str] = {}
        self.is_raw_texts = is_raw_texts
        self.doc_counter = 0

        # 加载停用词
        self.stopwords: Set[str] = set()
        if stopwords_path:
            self.load_stopwords(stopwords_path)

        # 加载用户词典
        if user_dict_path:
            jieba.load_userdict(user_dict_path)

    def load_stopwords(self, stopwords_path: str) -> None:
        """加载停用词"""
        with open(stopwords_path, "r", encoding="utf-8") as f:
            self.stopwords = set(line.strip() for line in f)

    def preprocess_text(self, text: str) -> str:
        """
        文本预处理
        """
        # 转换为小写
        text = text.lower()
        # 移除特殊字符
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)
        # 移除多余空格
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        """
        分词并移除停用词
        """
        words = jieba.lcut(text)
        one_char_size = len([i for i in words if len(i) == 1])
        all_size = len(words)
        if all_size != 0 and one_char_size / all_size > 0.6:
            words = [i for i in text.split() if i.strip()]

        # 过滤停用词和空字符
        words = [w for w in words if w not in self.stopwords and w.strip()]
        return words

    def create_minhash(self, words: List[str]) -> MinHash:
        """
        为分词结果创建 MinHash
        """
        minhash = MinHash(num_perm=self.num_perm)
        for word in words:
            minhash.update(word.encode("utf-8"))
        return minhash

    def add_document(self, text: str, doc_id: Optional[str] = None) -> str:
        """
        添加文档到索引

        Args:
            text: 文档文本
            doc_id: 文档ID（可选）

        Returns:
            doc_id: 文档ID
        """
        if doc_id is None:
            doc_id = f"doc_{self.doc_counter}"
            self.doc_counter += 1

        # 预处理和分词
        processed_text = self.preprocess_text(text)
        words = self.tokenize(processed_text)

        # 创建 MinHash
        minhash = self.create_minhash(words)
        if self.is_raw_texts:
            # 存储原始文本和 MinHash
            self.raw_texts[doc_id] = text
        # self.minhashes[doc_id] = minhash

        # 添加到 LSH
        self.lsh.insert(doc_id, minhash)

        return doc_id

    def batch_add_documents(self, texts: Dict[str, str]) -> None:
        """
        批量添加文档

        Args:
            texts: {doc_id: text} 的字典
        """
        for doc_id, text in texts.items():
            self.add_document(text, doc_id)

    def create_query_minhash(self, query: str):

        # 预处理查询文本
        processed_query = self.preprocess_text(query)
        query_words = self.tokenize(processed_query)
        # print(query_words)
        query_minhash = self.create_minhash(query_words)
        return query_minhash

    def find_similar(self, query_minhash: MinHash, return_similarities: bool = False) -> Union[
        List[str], List[Tuple[str, float]]]:
        """
        查找相似文档

        Args:
            query: 查询文本
            return_similarities: 是否返回相似度分数

        Returns:
            如果 return_similarities 为 True，返回 [(doc_id, similarity), ...]
            否则返回 [doc_id, ...]
        """

        # 使用 LSH 查找候选集
        similar_docs = self.lsh.query(query_minhash)

        # if return_similarities:
        #     # 计算精确的 Jaccard 相似度
        #     results = []
        #     for doc_id in similar_docs:
        #         similarity = query_minhash.jaccard(self.minhashes[doc_id])
        #         results.append((doc_id, similarity))
        #     # 按相似度降序排序
        #     return sorted(results, key=lambda x: x[1], reverse=True)

        return similar_docs

    def get_text(self, doc_id: str) -> Optional[str]:
        """获取原始文本"""
        if self.is_raw_texts:
            return self.raw_texts.get(doc_id)
        raise Exception("没有开启存储")

    def remove_document(self, doc_id: str) -> bool:
        """
        删除文档

        Returns:
            bool: 是否成功删除
        """
        # if doc_id not in self.minhashes:
        #     return False

        self.lsh.remove(doc_id)
        # del self.minhashes[doc_id]
        if self.is_raw_texts:
            del self.raw_texts[doc_id]
        return True

    def clear(self) -> None:
        """清空所有数据"""
        self.lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        # self.minhashes.clear()
        self.raw_texts.clear()
        self.doc_counter = 0


if __name__ == "__main__":
    # 创建匹配器实例
    matcher = TextMatcher(
        threshold=0.1,  # 相似度阈值
        num_perm=128,  # MinHash 排列数
    )

    # 添加单个文档
    doc_id = matcher.add_document(
        "北京是中国的首都"
    )

    # 批量添加文档
    docs = {"doc1": "北京是一座现代化的大都市", "doc2": "上海是中国最大的城市", "doc3": "中国的首都是北京"}
    matcher.batch_add_documents(docs)

    # 查找相似文档（不返回相似度分数）
    similar_docs = matcher.find_similar("北京首都")
    print("相似文档ID:", similar_docs)

    # 查找相似文档（返回相似度分数）
    similar_docs_with_scores = matcher.find_similar("北京首都", return_similarities=True)
    print("相似文档ID和分数:", similar_docs_with_scores)

    # 获取原始文本
    for doc_id, score in similar_docs_with_scores:
        print(f"文档 {doc_id}: {matcher.get_text(doc_id)} (相似度: {score:.2f})")

    # 删除文档
    matcher.remove_document("doc1")

    # 清空所有数据
    matcher.clear()

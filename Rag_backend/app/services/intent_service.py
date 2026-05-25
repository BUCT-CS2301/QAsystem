import re

from app.models import Intent


PROPERTY_KEYWORDS = {
    "material": ["材质", "材料", "质地", "什么做", "用什么"],
    "period": ["朝代", "时期", "年代", "哪个朝", "什么时代"],
    "type": ["品类", "类别", "类型", "种类", "是什么器"],
    "museum": ["博物馆", "馆藏", "收藏", "藏于", "在哪里", "在哪"],
    "image": ["图片", "照片", "图像", "展示图"],
    "dimensions": ["尺寸", "大小", "规格"],
    "description": ["介绍", "简介", "描述", "讲讲", "说明"],
    "accession_number": ["编号", "藏品号", "登记号"],
}

LIST_WORDS = ["哪些", "有什么", "有哪些", "列出", "查询", "找出"]
RELATED_WORDS = ["相似", "类似", "相关", "同类", "同材质", "同朝代", "推荐"]

STOP_WORDS = {
    "请", "帮我", "一下", "这个", "这件", "文物", "藏品", "博物馆", "有哪些", "哪些",
    "什么", "多少", "查询", "介绍", "告诉我", "相关", "相似", "类似", "的", "是", "吗",
}


class IntentService:
    def parse(self, question: str) -> Intent:
        normalized = question.strip()
        attribute = self._detect_attribute(normalized)

        if any(word in normalized for word in RELATED_WORDS):
            return Intent(name="related", attribute=attribute, keywords=self.extract_keywords(normalized))

        if any(word in normalized for word in LIST_WORDS):
            return Intent(name="list", attribute=attribute, keywords=self.extract_keywords(normalized))

        if attribute:
            return Intent(name="attribute", attribute=attribute, keywords=self.extract_keywords(normalized))

        return Intent(name="general", keywords=self.extract_keywords(normalized))

    def _detect_attribute(self, question: str) -> str | None:
        for attribute, keywords in PROPERTY_KEYWORDS.items():
            if any(keyword in question for keyword in keywords):
                return attribute
        return None

    def extract_keywords(self, question: str) -> list[str]:
        cleaned = question
        for words in PROPERTY_KEYWORDS.values():
            for word in words:
                cleaned = cleaned.replace(word, " ")
        for word in LIST_WORDS + RELATED_WORDS:
            cleaned = cleaned.replace(word, " ")
        for word in STOP_WORDS:
            cleaned = cleaned.replace(word, " ")

        parts = re.split(r"[\s,，。！？?；;：:、（）()《》<>【】\[\]\"']+", cleaned)
        keywords = []
        for part in parts:
            token = part.strip()
            if not token or token in STOP_WORDS:
                continue
            if len(token) > 30:
                token = token[:30]
            keywords.append(token)

        # 保留原问题片段，便于模糊匹配短问题。
        if not keywords and question.strip():
            keywords.append(question.strip()[:30])
        return list(dict.fromkeys(keywords))

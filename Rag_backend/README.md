# Museum RAG Project

这是一个基于知识图谱 (Neo4j) 和大语言模型 (DeepSeek) 构建的博物馆问答系统。

## 特性
- 支持基于 Neo4j 向量检索的 RAG 问答
- 支持属性实时提取、长下文流式回答生成
- 结合 MySQL 提供完备的文物属性
- 带 Redis 缓存层加速二次问答

## 安装与运行

1. 克隆代码后，安装依赖：
```bash
pip install -r requirements.txt
```

2. 准备环境变量：
将 `.env.example` 复制为 `.env`，并在其中填入您的数据库帐号密码和 API Keys（尤其是 `DEEPSEEK_API_KEY`）。

```bash
cp .env.example .env
```

3. 运行问答终端：
```bash
python main.py
```

# Museum RAG Project

这是一个基于知识图谱 (Neo4j) 和大语言模型 (DeepSeek) 构建的博物馆问答系统。

## 特性
- 支持基于 Neo4j 向量检索的 RAG 问答
- 支持属性实时提取、长下文流式回答生成
- 结合 MySQL 提供完备的文物属性
- 带 Redis 缓存层加速二次问答

## 安装与运行

### 1. 基础数据库准备 (前置条件)
本项目的初始底层数据库配置由另一个仓库负责。在运行本项目前，请先前往 [Knowledge-Graph 仓库](https://github.com/BUCT-CS2301/Knowledge-Graph.git) 部署并启动 Neo4j 和 MySQL 数据库，并完成初始知识图谱的构建。

### 2. 克隆与安装依赖
数据库启动后，克隆本项目，**进入后端服务端目录**，并安装相关依赖：
```bash
cd Rag_backend
pip install -r requirements.txt
```

### 3. 配置环境变量
将 `.env.example` 复制为 `.env`。根据你在第 1 步中启动的数据库的实际端口和账号，以及你的大模型 API Keys（特别是 `DEEPSEEK_API_KEY`），填入到 `.env` 文件中。
```bash
cp .env.example .env
```

### 4. 数据特征压缩与入库
在图谱数据库已运行且 `.env` 配置完毕后，运行内置脚本。该脚本将调用大模型生成文物的段落摘要与词向量，并将其压缩存回你的 Neo4j 数据库中，用于后续的 RAG 检索：
```bash
python scripts/embed_artifacts.py
```

### 5. 运行后端服务
如果一切顺利，即可启动问答 API 后端服务：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

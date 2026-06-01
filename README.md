# 智能文物问答系统 (Smart Artifact QA System)

基于知识图谱 (Knowledge Graph) 与大语言模型 (LLM) 结合的 RAG（检索增强生成）智能问答系统。专为博物馆与历史文物查询设计，提供准确、连贯的自然语言问答交互，支持流式输出以及详细的图文溯源。

## 🌟 核心特性

- **RAG 架构问答**：结合 Neo4j 图谱结构化知识及 Embedding 向量相似度检索，通过大模型生成高质量答案，极大降低大模型幻觉。
- **流式输出 (SSE)**：采用 Server-Sent Events (SSE) 协议提供类似 ChatGPT 的实时逐字打字体验。
- **双端分离架构**：
  - 前端：Vue 3 + Vite，响应式现代化界面设计。
  - 后端：FastAPI，高性能异步 API 服务。
- **图谱与关系数据双引擎**：通过 Neo4j 提供向量搜索及关系查询，配合 MySQL 提供详细的业务字段及多媒体数据（如图片 URL）。

## 🏗️ 技术栈

- **前端 (Frontend)**：Vue 3, Vite, Fetch API (SSE)
- **后端 (Backend)**：Python 3.10+, FastAPI, Uvicorn, Neo4j Python Driver, PyMySQL, ThreadPoolExecutor
- **数据库 (Databases)**：
  - Neo4j (向量存储与知识图谱)
  - MySQL (业务核心结构化数据管理)
- **大模型 (LLM)**：DeepSeek-V3 (文本生成), BAAI/bge-m3 (向量化 Embedding)

## 📁 项目结构

```text
.
├── Rag_backend/         # FastAPI 后端服务目录
│   ├── app/             # 核心业务逻辑 (API、服务层、数据访问)
│   ├── scripts/         # 运维脚本 (如 embed_artifacts.py 等)
│   ├── main.py          # FastAPI 入口文件
│   └── .env             # 后端环境变量配置文件
├── vue-project/         # Vue 3 前端界面目录
│   ├── src/             # 前端源代码 (视图、组件)
│   ├── vite.config.js   # Vite 配置文件及代理设置
│   └── package.json     # Node.js 依赖配置
└── documents/           # 项目及 API 文档 (如 API_DOC.md)
```

## 🚀 快速启动

### 1. 配置环境

系统依赖远程的 MySQL 和 Neo4j 数据库。请在 `Rag_backend/.env` 中配置相关的数据库和模型 Key：
```env
NEO4J_URI=bolt://39.106.231.119:7687
MYSQL_HOST=39.106.231.119
DEEPSEEK_API_KEY=sk-xxxxxx...
...
```

### 2. 启动后端 (FastAPI)

```bash
cd Rag_backend
pip install -r requirements.txt
python main.py
```
> 后端服务将默认启动在 `http://127.0.0.1:8000`

### 3. 启动前端 (Vue)

```bash
cd vue-project
npm install
npm run dev
```
> 前端服务将默认启动在 `http://localhost:5173`。Vite 代理已配置好自动将 `/api` 开头的请求转发至后端。

## 📜 接口文档

详细的接口对接文档请参阅：[API_DOC.md](./documents/API_DOC.md)
包含 `POST /api/chat` (SSE 流式) 与 `POST /qa/ask` (REST JSON) 的请求响应规范。

## 🧑‍💻 贡献指南

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 将您的更改推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

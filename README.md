# Multi-Agent AI 研究助手

基于 LangGraph 的多智能体协作系统，用于自动化内容生成、代码编写和数据分析。

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1.5-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)

## 功能特性

- 多智能体协作：Researcher、Writer、Reviewer、Code Generator、Data Analyst
- 智能任务路由：基于 LLM 语义识别，自动选择合适的 Agent
- 流式输出：实时显示生成进度
- 用户认证：基于 Token 的安全认证
- 历史记录：保存和查看历史报告
- 内容清理：自动清理 LLM 生成的内容格式
- 缓存优化：任务类型识别缓存，提升性能

## 技术栈

### 后端
- FastAPI - Web 框架
- LangGraph - 工作流编排
- LangChain - LLM 集成
- SQLAlchemy - ORM
- MySQL - 数据库

### 前端
- Streamlit - Web UI

### AI 模型
- DeepSeek - LLM 提供商

## 项目结构

```
MultiAgent-Research/
├── client_app.py          # Streamlit 前端
├── main.py               # FastAPI 主应用
├── graph/
│   ├── state.py          # 工作流状态定义
│   └── workflow.py       # LangGraph 工作流
├── nodes/
│   ├── research.py       # 搜索 Agent
│   ├── code_generator.py # 代码生成 Agent
│   ├── data_analyst.py  # 数据分析 Agent
│   ├── write.py         # 写作 Agent
│   └── reviewer.py      # 审核 Agent
├── routers/
│   ├── auth.py          # 认证路由
│   └── report.py        # 报告路由
├── crud/
│   ├── user.py          # 用户 CRUD
│   └── report.py        # 报告 CRUD
├── models/
│   ├── users.py         # 数据模型
│   └── report.py        # 报告模型
├── utils/
│   ├── my_llm.py       # LLM 初始化
│   ├── agent_tools.py   # 搜索工具
│   └── content_cleaner.py # 内容清理
├── config/
│   └── db_conf.py       # 数据库配置
├── requirements.txt       # 项目依赖
├── Dockerfile           # Docker 构建文件
├── docker-compose.yml   # Docker 编排文件
└── .gitignore          # Git 忽略文件
```

## 快速开始

### 环境要求

- Python 3.12+
- MySQL 8.0+
- DeepSeek API Key

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件：

```env
deepseek-api-key=your_api_key
deepseek-api-base=https://api.deepseek.com
deepseek-model-name=deepseek-chat
database_url=mysql+aiomysql://user:password@localhost:3306/multiagent
secret_key=your_secret_key
algorithm=HS256
```

### 启动后端

```bash
python main.py
```

后端运行在：http://localhost:8000

### 启动前端

```bash
streamlit run client_app.py
```

前端运行在：http://localhost:8501

## Docker 部署

### 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Dockerfile

```bash
# 构建镜像
docker build -t multiagent-research .

# 运行容器
docker run -p 8000:8000 -p 8501:8501 --env-file .env multiagent-research
```

## 使用说明

### 1. 用户注册/登录

首次使用需要注册账号，登录后获得 Token 用于后续请求。

### 2. 提交任务

在输入框中输入任务，例如：
- "用Python实现快速排序算法"
- "分析2025年AI技术发展趋势"
- "写一篇关于人工智能的文章"

### 3. 智能路由

系统会自动识别任务类型：
- **代码任务** → Code Generator → Writer → Reviewer
- **数据任务** → Data Analyst → Writer → Reviewer
- **标准任务** → Writer → Reviewer

### 4. 审核与修改

如果 Reviewer 认为需要修改，会自动返回 Writer 重写，直到通过。

### 5. 查看历史

可以查看所有历史报告，点击查看详情。

## Agent 说明

### Researcher（搜索 Agent）
- 功能：搜索相关信息
- 工具：ZhipuAI Web Search
- 输出：搜索结果列表

### Code Generator（代码生成 Agent）
- 功能：生成 Python 代码
- 特点：包含注释、错误处理、使用示例
- 清理：自动移除 markdown 标记和执行说明

### Data Analyst（数据分析 Agent）
- 功能：分析数据并生成报告
- 输出：Markdown 格式的分析报告

### Writer（写作 Agent）
- 功能：基于搜索结果和代码撰写文章
- 特点：结构完整、逻辑清晰
- 清理：自动修复格式问题

### Reviewer（审核 Agent）
- 功能：审核文章质量
- 决策：通过或要求修改
- 标准：内容质量、结构完整性

## 核心技术

### LangGraph 工作流

```python
# 状态定义
class AgentState(TypedDict):
    task: str
    search_results: List[str]
    draft: str
    code: str
    critique: str
    revision_count: int

# 工作流定义
workflow = StateGraph(AgentState)
workflow.add_node("researcher", research_node)
workflow.add_edge("researcher", "writer")
app = workflow.compile()
```

### 内容清理

```python
# 清理代码
clean_code_output(code)

# 清理文章
clean_article_output(article)

# 清理搜索词
clean_search_query(query)
```

### 任务类型识别

```python
# 使用 LLM 语义识别
@lru_cache(maxsize=128)
def determine_task_type_cached(task: str) -> str:
    # 调用 LLM 判断任务类型
    # 返回：code/data/standard
```

## API 文档

### 认证接口

- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户

### 报告接口

- `POST /report/chat/stream` - 流式生成报告
- `GET /report/history` - 获取历史报告
- `GET /report/history/{id}` - 获取报告详情

## 开发说明

### 添加新 Agent

1. 在 `nodes/` 创建新文件
2. 实现 Agent 函数
3. 在 `graph/workflow.py` 添加节点
4. 配置路由逻辑

### 修改清理规则

编辑 `utils/content_cleaner.py`，添加或修改清理逻辑。

### 切换 LLM

修改 `utils/my_llm.py`，配置新的 API Key 和模型。

## 常见问题

### Q: Docker 启动失败

A: 确保已安装 Docker Desktop，并检查状态是否为"Running"。

### Q: Token 过期

A: 系统会自动检测并提示重新登录。

### Q: 生成内容格式错误

A: 系统会自动清理，确保格式正确。

## 许可证

MIT License


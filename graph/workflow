from functools import lru_cache
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from nodes.research import research_node
from nodes.code_generator import code_generator_node
from nodes.data_analyst import data_analyst_node
from nodes.write import writer_node
from nodes.reviewer import reviewer_node
from utils.my_llm import llm
from langchain_core.prompts import ChatPromptTemplate

@lru_cache(maxsize=128)
def determine_task_type_cached(task:str):
    """
    使用 LLM 识别任务类型
    返回: 'code' | 'data' | 'standard'
    """
    
    prompt = ChatPromptTemplate.from_template("""请分析以下任务，判断它属于哪种类型。

任务：{task}

类型定义：
- code：涉及代码编写、算法实现、编程、函数开发等
-  data：涉及数据分析、统计、趋势分析、图表制作、可视化等
- standard：普通文章写作、内容创作、知识总结等

只返回类型名称（code/data/standard），不要其他内容。""")
    
    chain = prompt | llm
    response = chain.invoke({"task": task})
    
    task_type = response.content.strip().lower()
    
    # 确保返回的是有效类型
    if task_type not in ['code', 'data', 'standard']:
        task_type = 'standard'
    
    return task_type

def determine_task_type(state: AgentState):
    """
    包装缓存函数，用于LangGraph调用
    """
    task = state.get('task', '')
    return determine_task_type_cached(task)
    
def check_critique(state: AgentState):
    """
    检查审稿意见是否通过，若通过则结束，否则需要修改
    """
    if state.get("critique") == "APPROVE":
        return "end"
    return "rewrite"

# 创建高级工作流
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("researcher", research_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("code_generator", code_generator_node)
workflow.add_node("data_analyst", data_analyst_node)

# 设置入口
workflow.set_entry_point("researcher")

# 添加条件边：根据任务类型选择不同路径
workflow.add_conditional_edges(
    "researcher",
    determine_task_type,
    {
        "code": "code_generator",    # 代码任务 → 代码生成Agent
        "data": "data_analyst",      # 数据任务 → 数据分析Agent
        "standard": "writer"         # 标准任务 → 写作Agent
    }
)

# 代码生成路径
workflow.add_edge("code_generator", "writer")

# 数据分析路径
workflow.add_edge("data_analyst", "writer")

# 写作 → 审核
workflow.add_edge("writer", "reviewer")

# 审核结果：通过或重写
workflow.add_conditional_edges(
    "reviewer",
    check_critique,
    {
        "end": END,
        "rewrite": "writer"
    }
)

# 编译图
app = workflow.compile()

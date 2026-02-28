from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate

from graph.state import AgentState
from utils.my_llm import llm


def data_analyst_node(state: AgentState):
    """
    数据分析节点:分析搜索结果中的数据
    """
    print("--- Data Analyst: 正在分析数据 ---")
    
    task = state.get('task', '')
    search_results = state.get('search_results', [])
    
    prompt_text = """你是一名数据分析师。请分析以下信息中的数据。

任务：
{task}

信息：
{search_results}

要求：
1. 识别关键数据点
2. 提供统计分析
3. 生成数据洞察
4. 如果可能，建议可视化方式
5. 直接输出分析报告，不要输出JSON格式
6. 以Markdown格式输出，包含标题、关键点、建议等

输出格式示例：
# 数据分析报告

## 总结
（总结内容）

## 关键数据点
1. 数据点1
2. 数据点2

## 洞察和建议
（洞察和建议内容）
"""
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    response = chain.invoke({
        "task": task,
        "search_results": "\n".join(search_results)
    })
    
    analysis_report = response.content
    
    # 记录Agent执行历史
    history = state.get('agent_history', [])
    history.append({
        "agent": "data_analyst",
        "action": "analyze_data",
        "timestamp": datetime.now().isoformat(),
        "input": task,
        "report_length": len(analysis_report)
    })
    
    # 数据分析任务：直接返回分析报告作为draft
    return {"data_analysis": {"report": analysis_report}, "draft": analysis_report, "agent_history": history}

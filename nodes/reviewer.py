from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

from graph.state import AgentState
from utils.my_llm import llm


def reviewer_node(state: AgentState):
    """
    审核节点:根据草稿内容和任务要求进行审核
    """
    print("--- Reviewer: 正在审核 ---")
    
    draft = state.get('draft', '')
    task = state.get('task', '')
    search_results = state.get('search_results', [])
    revision_count = state.get('revision_count', 0)

    # Allow maximum 3 revisions to prevent infinite loops
    if revision_count >= 3:
        print("--- Reviewer: 达到最大修改次数，强制通过 ---")
        
        # 记录Agent执行历史
        history = state.get('agent_history', [])
        history.append({
            "agent": "reviewer",
            "action": "review",
            "timestamp": datetime.now().isoformat(),
            "result": "force_approve",
            "reason": "max_revisions_reached"
        })
        
        return {"critique": "APPROVE", "agent_history": history}
    
    prompt_text = """你是一名严格的主编。请审核以下关于 "{task}" 的文章草稿。

参考资料：
{search_results}

草稿内容：
{draft}

要求：
1. 根据用户要求和检索到的参考资料检查草稿内容是否充实，逻辑是否严密。
2. 如果文章质量合格，请只输出 "APPROVE" (不带引号)。
3. 如果需要修改，请给出具体的修改建议（critique），不要太长，直接指出问题。
"""
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    response = chain.invoke({
        "task": task,
        "draft": draft,
        "search_results": "\n".join(search_results)
    })
    
    critique = response.content.strip()
    
    # Simple check if LLM approved it
    if "APPROVE" in critique:
        result = "APPROVE"
    else:
        result = critique
    
    # 记录Agent执行历史
    history = state.get('agent_history', [])
    history.append({
        "agent": "reviewer",
        "action": "review",
        "timestamp": datetime.now().isoformat(),
        "result": result,
        "revision_count": revision_count
    })
    
    return {"critique": result, "agent_history": history}

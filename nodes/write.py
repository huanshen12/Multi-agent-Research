from datetime import datetime
import json
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState
from utils.my_llm import llm
from utils.content_cleaner import clean_article_output


def writer_node(state: AgentState):
    """
    写节点:根据搜索内容和修改意见撰写草稿
    """
    print("--- Writer: 正在撰写草稿 ---")
    
    current_revision = state.get('revision_count', 0)
    new_revision_count = current_revision + 1
    
    task = state.get('task', '')
    search_results = state.get('search_results', [])
    critique = state.get('critique', '')
    data_analysis = state.get('data_analysis', {})
    code = state.get('code', '')

    prompt_text = """你是一名专业的技术撰稿人。请根据以下信息撰写一篇技术文章。

任务：{task}

参考资料：
{search_results}

要求：
1. 文章主题围绕任务：{task}
2. 内容基于搜索结果，进行整合和扩展
3. 语言通顺，逻辑清晰，结构完整
4. 使用markdown格式
5. 这是第 {revision_count} 版草稿
"""
    
    # 如果有代码，添加说明
    if code:
        prompt_text += """

注意：已有相关代码实现，请在文章中适当展示代码，使用markdown代码块格式（```python ... ```）。
"""
    
    if critique:
        prompt_text += f"""

上一版的审核意见：{critique}
"""
        
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    # 准备参数
    invoke_params = {
        "task": task,
        "search_results": "\n".join(search_results),
        "revision_count": new_revision_count,
        "critique": critique
    }
    
    response = chain.invoke(invoke_params)
    
    # 后处理清理
    draft = clean_article_output(response.content)
    
    # 记录Agent执行历史
    history = state.get('agent_history', [])
    history.append({
        "agent": "writer",
        "action": "write_draft",
        "timestamp": datetime.now().isoformat(),
        "input": task,
        "revision": new_revision_count,
        "draft_length": len(draft)
    })
    
    return {
        "draft": draft,
        "revision_count": new_revision_count,
        "agent_history": history
    }

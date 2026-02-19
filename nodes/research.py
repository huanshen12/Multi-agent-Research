from datetime import datetime
from graph.state import AgentState
from utils.agent_tools import tavily_search
from utils.content_cleaner import clean_search_query


def research_node(state: AgentState):
    """
    搜索节点:通过搜索工具来获取信息
    """
    print("--- Researcher: 正在搜索信息 ---")
    task = state.get('task', '')
    
    # 清理搜索查询
    search_query = clean_search_query(task)
    
    print(f"搜索查询: {search_query}")
    
    results = tavily_search.invoke(search_query)
    
    # 记录Agent执行历史
    history = state.get('agent_history', [])
    history.append({
        "agent": "researcher",
        "action": "search",
        "timestamp": datetime.now().isoformat(),
        "input": task,
        "search_query": search_query,
        "output_count": len(results)
    })
    
    return {"search_results": results, "agent_history": history}

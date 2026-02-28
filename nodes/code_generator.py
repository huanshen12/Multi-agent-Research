from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from utils.my_llm import llm
from graph.state import AgentState
from utils.content_cleaner import clean_code_output


def code_generator_node(state: AgentState):
    """
    代码生成节点:根据任务生成代码
    """
    print("--- Code Generator: 正在生成代码 ---")
    
    task = state.get('task', '')
    search_results = state.get('search_results', [])
    
    prompt_text = """你是一名资深软件工程师。请根据以下任务生成Python代码。

任务：{task}

参考资料：
{search_results}

要求：
1. 生成完整、可运行的代码
2. 添加必要的注释
3. 包含错误处理
4. 包含使用示例
5. 代码风格符合最佳实践
6. 如果是算法题，在注释中提供时间复杂度分析
"""
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    response = chain.invoke({
        "task": task,
        "search_results": "\n".join(search_results)
    })
    
    code = response.content
    
    # 后处理清理
    code = clean_code_output(code)
    
    # 记录Agent执行历史
    history = state.get('agent_history', [])
    history.append({
        "agent": "code_generator",
        "action": "generate_code",
        "timestamp": datetime.now().isoformat(),
        "input": task,
        "code_length": len(code)
    })
    
    return {"code": code, "draft": code, "agent_history": history}
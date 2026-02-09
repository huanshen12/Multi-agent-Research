from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from graph.state import AgentState
from tools.search_tool import tavily_search
import os 
import dotenv
dotenv.load_dotenv()


llm = ChatOpenAI(model=os.getenv("deepseek-model-name"),
                 api_key=os.getenv("deepseek-api-key"),
                 base_url=os.getenv("deepseek-api-base"), 
                 temperature=0.5)

def research_node(state: AgentState):
    """
    Researcher node: uses search tool to gather information.
    """
    print("--- Researcher: 正在搜索信息 ---")
    task = state.get('task', '')
    # Directly invoke the tool since it's a mock for now, but in real scenario
    # this could also be an LLM decision point.
    results = tavily_search.invoke(task)
    return {"search_results": results}

def writer_node(state: AgentState):
    """
    Writer node: generates a draft based on search results using LLM.
    """
    print("--- Writer: 正在撰写草稿 ---")
    
    current_revision = state.get('revision_count', 0)
    # Increment revision count
    new_revision_count = current_revision + 1
    
    task = state.get('task', '')
    search_results = state.get('search_results', [])
    critique = state.get('critique', '')
    
    # Prompt for the writer
    # If there is a critique, include it in the prompt to improve the draft
    prompt_text = """你是一名专业的技术撰稿人。请根据以下信息撰写一篇关于 "{task}" 的简短文章。

搜索结果：
{search_results}

要求：
1. 内容必须基于搜索结果。
2. 语言通顺，逻辑清晰。
3. 这是一个第 {revision_count} 版草稿。
"""
    
    if critique:
        prompt_text += f"\n上一版的审核意见（请务必针对性修改）：\n{critique}"
        
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    response = chain.invoke({
        "task": task,
        "search_results": "\n".join(search_results),
        "revision_count": new_revision_count,
        "critique": critique
    })
    
    return {
        "draft": response.content,
        "revision_count": new_revision_count
    }

def reviewer_node(state: AgentState):
    """
    Reviewer node: critiques the draft using LLM.
    """
    print("--- Reviewer: 正在审核 ---")
    
    draft = state.get('draft', '')
    task = state.get('task', '')
    revision_count = state.get('revision_count', 0)

    # Allow maximum 3 revisions to prevent infinite loops
    if revision_count >= 3:
        print("--- Reviewer: 达到最大修改次数，强制通过 ---")
        return {"critique": "APPROVE"}
    
    prompt_text = """你是一名严格的主编。请审核以下关于 "{task}" 的文章草稿。

草稿内容：
{draft}

要求：
1. 检查内容是否充实，逻辑是否严密。
2. 如果文章质量合格，请只输出 "APPROVE" (不带引号)。
3. 如果需要修改，请给出具体的修改建议（critique），不要太长，直接指出问题。
"""
    
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm
    
    response = chain.invoke({
        "task": task,
        "draft": draft
    })
    
    critique = response.content.strip()
    
    # Simple check if LLM approved it
    if "APPROVE" in critique:
        return {"critique": "APPROVE"}
    else:
        return {"critique": critique}

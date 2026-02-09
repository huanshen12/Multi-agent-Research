
import operator
from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    为多agent工作流创建state
    """
    task: str                      #用户提出的任务
    search_results: List[str]       #搜索工具返回的结果
    draft: str                      #草稿内容   
    critique: str                   #审稿提出的意见
    revision_count: int             #修订次数
    messages: Annotated[List[BaseMessage], operator.add]   #消息列表，用于存储所有交互消息

from langchain_core.tools import tool
from zai import ZhipuAiClient
import os
import dotenv
dotenv.load_dotenv()

client = ZhipuAiClient(api_key=os.getenv("zhipu-api-key"))


@tool
def tavily_search(query: str) -> list[str]:
    """
    使用数据进行搜索。
    在生产环境中，应在此处实现真实的搜索逻辑。
    """
    try:
        response = client.web_search.web_search(
        search_engine="search_std",
        search_query=query,
<<<<<<< HEAD
        count=5,  # 返回结果的条数，范围1-50，默认5
=======
        count=10,  # 返回结果的条数，范围1-50，默认10
>>>>>>> 904fced4bb476c788822e27e54df29628f8ac02e
        search_domain_filter=None,  # 只访问指定域名的内容
        search_recency_filter="noLimit",  # 搜索指定日期范围内的内容
        content_size="low"  # 控制网页摘要的字数，默认medium
        )
        result = []
        for res in response.search_result:
            result.append(res.content)
        print(result)
        return result
    except Exception as exc:
        print(f"error: {str(exc)}")
    # print(f"正在执行模拟搜索：{query}")
    
    # # 模拟返回数据：关于 "2025 AI 发展趋势" 的三条假新闻
    # return [
    #     "1. 到2025年，Agentic AI（代理AI）将成为主流，自主Agent在无需人类干预的情况下处理复杂工作流。",
    #     "2. 由于专用硬件的突破，LLM 推理成本下降了90%，使得在边缘设备上进行本地部署成为可能。",
    #     "3. 多模态模型实现了近乎完美的推理能力，彻底改变了科学研究的自动化进程。"
    # ]

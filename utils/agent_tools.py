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
        print(f"[DEBUG] 开始搜索: {query}")
        print(f"[DEBUG] API Key: {os.getenv('zhipu-api-key')[:10]}...")
        
        response = client.web_search.web_search(
            search_engine="search_std",
            search_query=query,
            count=10,  # 返回结果的条数，范围1-50，默认10
            search_domain_filter=None,  # 只访问指定域名的内容
            search_recency_filter="noLimit",  # 搜索指定日期范围内的内容
            content_size="low"  # 控制网页摘要的字数，默认medium
        )
        result = []
        for res in response.search_result:
            result.append(res.content)
        print(f"[DEBUG] 搜索结果数量: {len(result)}")
        return result
    except Exception as exc:
        print(f"[ERROR] 搜索失败: {type(exc).__name__}: {str(exc)}")
        import traceback
        traceback.print_exc()
        return []

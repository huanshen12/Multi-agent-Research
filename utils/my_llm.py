import os 
import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()


llm = ChatOpenAI(model=os.getenv("deepseek-model-name"),
                 api_key=os.getenv("deepseek-api-key"),
                 base_url=os.getenv("deepseek-api-base"),
                 temperature=0.5)


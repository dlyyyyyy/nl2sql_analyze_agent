import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_deepseek import ChatDeepSeek
from langchain_community.agent_toolkits import create_sql_agent

# 加载 .env 中的环境变量
load_dotenv()

# 验证 API Key 是否加载成功
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中正确设置")

# 连接数据库
db = SQLDatabase.from_uri("sqlite:///sales.db")

# 初始化 DeepSeek 模型
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=api_key,
    temperature=0.1
)

# 创建工具包
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 创建 Agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True
)

def ask_question(question: str):
    try:
        response = agent.invoke({"input": question})
        return response['output']
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    test_questions = [
        "Which product had the highest collection amount last month?",
        "What is the average collection rate in Beijing?",
        "Rank the regions by total collection amount."
    ]
    for q in test_questions:
        print(f"\nUser: {q}")
        print(f"Agent: {ask_question(q)}\n")
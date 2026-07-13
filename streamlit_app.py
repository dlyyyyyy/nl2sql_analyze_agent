import os
import streamlit as st
import json  # ← 新增
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_deepseek import ChatDeepSeek
from langchain_community.agent_toolkits import create_sql_agent

# 页面配置（宽屏、图标）
st.set_page_config(page_title="智能数据分析Agent", page_icon="🤖", layout="wide")

# 自定义CSS，让气泡更好看
st.markdown("""
<style>
    .stChatMessage {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin-bottom: 0.5rem;
        max-width: 80%;
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #f0f0f0;
        margin-right: auto;
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #dcf8c6;
        margin-left: auto;
    }
</style>
""", unsafe_allow_html=True)

# 加载环境变量
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    st.error("请在 .env 文件中配置 DEEPSEEK_API_KEY")
    st.stop()

# 连接数据库
db = SQLDatabase.from_uri("sqlite:///sales.db")

# 初始化模型
llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key, temperature=0.1)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=False, handle_parsing_errors=True)

# ====== 新增：推荐问题生成函数 ======
def generate_recommended_questions(user_question: str, agent_answer: str) -> list:
    prompt = f"""
你是一个数据分析助手。用户刚才问了下面这个问题，我给出了回答。

用户问题：{user_question}
我的回答：{agent_answer}

请根据以上对话，生成3个用户可能继续追问的相关问题。
要求：
- 只输出JSON数组，不要任何其他文字
- 问题要贴近业务，覆盖不同角度（如时间对比、区域拓展、关联分析）
- 格式示例：["问题1", "问题2", "问题3"]

输出：
"""
    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        if raw.startswith("```json"):
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif raw.startswith("```"):
            raw = raw.split("```")[1].split("```")[0].strip()
        questions = json.loads(raw)
        return questions[:3]
    except Exception as e:
        print(f"生成推荐问题失败: {e}")
        return []

# 标题和说明
st.title("💬 智能数据分析Agent")
st.caption("用自然语言提问，例如：“北京地区回款额最高的产品是什么？”")

# 初始化历史消息
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是数据分析助手。你可以问我关于销售回款的问题，比如：\n- 哪个产品回款额最高？\n- 各区域回款排名？\n- 北京的平均回款率是多少？"}
    ]

# 显示历史对话
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 示例问题（快捷按钮）
cols = st.columns(3)
example_questions = [
    "哪个产品回款额最高？",
    "各区域回款总额排名",
    "北京的平均回款率"
]
for idx, q in enumerate(example_questions):
    if cols[idx].button(q, key=f"ex_{idx}"):
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        with st.chat_message("assistant"):
            with st.spinner("正在查询..."):
                try:
                    response = agent.invoke({"input": q})
                    answer = response['output']
                except Exception as e:
                    answer = f"出错：{str(e)}"
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

# 底部输入框
if prompt := st.chat_input("输入你的数据问题..."):
    # 用户消息（右侧）
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    # 助手消息（左侧）
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = agent.invoke({"input": prompt})
                answer = response['output']
            except Exception as e:
                answer = f"出错：{str(e)}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # ====== 新增：生成并展示推荐问题 ======
    with st.chat_message("assistant"):
        with st.spinner("正在生成推荐问题..."):
            recommended = generate_recommended_questions(prompt, answer)
        if recommended:
            st.caption("💡 你可能还想问：")
            for q in recommended:
                st.markdown(f"- {q}")

    st.rerun()
import streamlit as st
import requests
import json
import os

# 设置页面配置
st.set_page_config(page_title="Multi-Agent AI 研究员 (SSE)", layout="wide", page_icon="🤖")

# API 基础 URL - 从环境变量读取，默认使用 localhost
API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 初始化会话状态
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

def make_authenticated_request(method, endpoint, **kwargs):
    """发送带认证的请求，自动处理 token 失效"""
    if not st.session_state.token:
        logout()
        return None
    
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {st.session_state.token}"
    kwargs["headers"] = headers
    
    try:
        response = requests.request(method, f"{API_BASE_URL}{endpoint}", **kwargs)
        
        if response.status_code == 401:
            st.warning("🔐 Token 已过期或无效，请重新登录")
            logout()
            return None
        
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {str(e)}")
        return None

def logout():
    """登出并清除会话状态"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.username = None
    if "messages" in st.session_state:
        del st.session_state.messages
    st.rerun()

# 登录页面
def login_page():
    st.title("🔐 用户登录")
    
    tab1, tab2 = st.tabs(["登录", "注册"])
    
    # 登录
    with tab1:
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="请输入用户名")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            submit = st.form_submit_button("登录")
            
            if submit:
                if not username or not password:
                    st.error("请填写完整信息")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/user/login",
                            json={"username": username, "password": password}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.logged_in = True
                            st.session_state.token = data.get("token")
                            st.session_state.username = username
                            st.success("登录成功！")
                            st.rerun()
                        else:
                            error_data = response.json()
                            st.error(f"登录失败: {error_data.get('detail', '未知错误')}")
                    except Exception as e:
                        st.error(f"连接失败: {str(e)}")
    
    # 注册
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("用户名", placeholder="请输入用户名（8-20位）")
            new_password = st.text_input("密码", type="password", placeholder="请输入密码（6-20位）")
            confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
            submit = st.form_submit_button("注册")
            
            if submit:
                if not new_username or not new_password or not confirm_password:
                    st.error("请填写完整信息")
                elif len(new_username) < 8 or len(new_username) > 20:
                    st.error("用户名长度必须在 8-20 位之间")
                elif len(new_password) < 6 or len(new_password) > 20:
                    st.error("密码长度必须在 6-20 位之间")
                elif new_password != confirm_password:
                    st.error("两次输入的密码不一致")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/user/register",
                            json={"username": new_username, "password": new_password}
                        )
                        
                        if response.status_code == 200:
                            st.success("注册成功！请切换到登录页面登录")
                        else:
                            error_data = response.json()
                            st.error(f"注册失败: {error_data.get('detail', '未知错误')}")
                    except Exception as e:
                        st.error(f"连接失败: {str(e)}")

# 主界面
def main_page():
    # 侧边栏
    with st.sidebar:
        st.title("🤖 AI 研究员")
        
        # 用户信息
        st.markdown("---")
        st.markdown("### 👤 用户信息")
        st.info(f"**用户名**: {st.session_state.username}")
        
        # 登出按钮
        if st.button("🚪 登出"):
            logout()
        
        st.markdown("---")
        
        # 功能导航
        st.header("功能导航")
        page = st.radio(
            "选择页面",
            ["💬 新建研究", "📚 历史报告", "⚙️ 设置"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 关于")
        st.info("""
        这是一个基于 Multi-Agent 的 AI 研究助手，可以自动搜集信息、撰写报告并进行审核。
        """)
    
    # 主页面
    st.title("🤖 Multi-Agent AI 研究员 (SSE版)")
    
    # 根据选择的页面显示不同内容
    if page == "💬 新建研究":
        st.markdown("输入您的研究任务，观察 AI 代理团队如何协同工作。")
        
        # 初始化会话状态用于存储聊天记录
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 显示聊天历史
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        def parse_sse_line(line):
            """Simple parser for SSE data lines."""
            line = line.strip()
            if not line:
                return None
            if line.startswith(b"data: "):
                data_str = line[6:].decode("utf-8")
                if data_str == "[DONE]":
                    return {"type": "done"}
                try:
                    return json.loads(data_str)
                except json.JSONDecodeError:
                    return None
            return None

        # 获取用户输入
        if prompt := st.chat_input("请输入您的研究任务（例如：2025年AI发展趋势）..."):
            # 模拟用户消息并显示
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 创建助手消息容器
            with st.spinner("AI 代理团队正在工作..."):
                with st.chat_message("assistant"):
                    # 创建执行历史容器
                    with st.expander("📋 Agent 执行历史", expanded=True):
                        history_container = st.container()
                    
                    # 创建占位符
                    status_placeholder = st.empty()
                    content_placeholder = st.empty()
                    full_response = ""
                    execution_history = []
                    
                    try: 
                        # 发送 POST 请求并开启流式接收
                        response = make_authenticated_request(
                            "POST",
                            "/report/chat/stream",
                            json={"query": prompt},
                            stream=True
                        )
                        
                        if response and response.status_code == 200:
                            # 循环读取流式响应
                            for line in response.iter_lines():
                                if line:
                                    event_data = parse_sse_line(line)
                                    if event_data:
                                        msg_type = event_data.get("type")
                                        content = event_data.get("content", "")
                                        
                                        if msg_type == "status":
                                            # 添加到执行历史
                                            execution_history.append(content)
                                            # 更新执行历史显示
                                            with history_container:
                                                st.markdown("### 执行步骤")
                                                for idx, step in enumerate(execution_history, 1):
                                                    st.markdown(f"{idx}. {step}")
                                            
                                        elif msg_type == "token":
                                            # 累加内容并显示（打字机效果）
                                            full_response += content
                                            # 在末尾添加光标以增强打字机效果
                                            content_placeholder.markdown(full_response + "▌")
                                            
                                        elif msg_type == "error":
                                            st.error(f"❌ 发生错误: {content}")
                                            break
                                            
                                        elif msg_type == "done":
                                            break
                                            
                            # 清除状态信息并展示最终结果（移除光标）
                            status_placeholder.empty()
                            content_placeholder.markdown(full_response)
                            
                            # 保存助手回复到历史记录
                            if full_response:
                                st.session_state.messages.append({"role": "assistant", "content": full_response})
                        else:
                            st.error(f"请求失败: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"连接失败: {str(e)}")

    elif page == "📚 历史报告":
        st.markdown("## 📚 历史研究报告")
        
        # 加载历史报告
        with st.spinner("正在加载历史报告..."):
            response = make_authenticated_request("GET", "/report/chat/history")
            
            if response and response.status_code == 200:
                data = response.json()
                
                if data.get("success") and data.get("data"):
                    reports = data["data"]
                    
                    if not reports:
                        st.info("暂无历史报告，快去创建一个吧！")
                    else:
                        # 按创建时间倒序排列
                        reports.sort(key=lambda x: x["created_at"] or "", reverse=True)
                        
                        # 显示报告列表
                        for idx, report in enumerate(reports):
                            report_id = report["id"]
                            topic = report["topic"]
                            content = report["content"]
                            created_at = report["created_at"]
                            
                            # 创建一个可展开的区域
                            with st.expander(f"📄 {topic}", expanded=False):
                                # 显示创建时间
                                if created_at:
                                    st.caption(f"创建时间: {created_at}")
                                
                                # 显示报告内容
                                st.markdown(content)
                                
                                # 添加操作按钮
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("📋 复制内容", key=f"copy_{report_id}"):
                                        st.code(content, language=None)
                                        st.success("内容已显示，可以手动复制")
                                
                                with col2:
                                    if st.button("🗑️ 删除报告", key=f"delete_{report_id}"):
                                        st.warning("删除功能开发中...")
                                
                                st.markdown("---")
                else:
                    st.info("暂无历史报告")
            elif response:
                st.error(f"加载失败: {response.status_code}")

    elif page == "⚙️ 设置":
        st.markdown("## ⚙️ 系统设置")
        st.info("设置功能开发中...")

# 主程序
if not st.session_state.logged_in:
    login_page()
else:
    main_page()

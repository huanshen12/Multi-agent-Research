import json
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse
from config.db_conf import get_db
from crud.report import save_report
from crud.report import get_history_report_list
from crud.user import get_current_user
from models.users import User
from schema.report import ChatRequest
from graph.workflow import app as workflow_app


router = APIRouter(prefix="/report/chat",tags=["报告"])

async def get_token_from_header(authorization: str = Header(...)):
    """从请求头中提取 token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")
    return authorization[7:]

async def get_current_user_dependency(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户（依赖注入版本）"""
    return await get_current_user(token, db)

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """
    使用 Server-Sent Events (SSE) 流式返回生成结果，并保存到数据库
    """
    
    async def event_generator():
        task = request.query
        print(f"收到用户任务: {task}")
        
        # 发送初始状态
        yield f"data: {json.dumps({'type': 'status', 'content': '任务已接收，正在启动工作流...'}, ensure_ascii=False)}\n\n"
        
        # 初始化状态
        initial_state = {
            "task": task,
            "revision_count": 0,
            "search_results": [],
            "messages": []
        }
        
        final_state = None
        current_draft_content = ""
        
        try:
            # 使用 astream_events 允许细粒度的事件流式传输
            async for event in workflow_app.astream_events(initial_state, version="v2"):
                kind = event["event"]
                name = event.get("name", "")
                
                # --- 处理 LangGraph 节点开始事件 ---
                if kind == "on_chain_start":
                    if name == "researcher":
                        yield f"data: {json.dumps({'type': 'status', 'content': '🔍 研究员正在搜集信息...'}, ensure_ascii=False)}\n\n"
                    elif name == "code_generator":
                        yield f"data: {json.dumps({'type': 'status', 'content': '💻 代码生成器正在编写代码...'}, ensure_ascii=False)}\n\n"
                    elif name == "data_analyst":
                        yield f"data: {json.dumps({'type': 'status', 'content': '📊 数据分析师正在分析数据...'}, ensure_ascii=False)}\n\n"
                    elif name == "writer":
                        yield f"data: {json.dumps({'type': 'status', 'content': '✍️ 撰稿人正在撰写初稿...'}, ensure_ascii=False)}\n\n"
                        # 重置当前草稿内容（新的一版）
                        current_draft_content = ""
                    elif name == "reviewer":
                        yield f"data: {json.dumps({'type': 'status', 'content': '👀 审稿人正在审核文章...'}, ensure_ascii=False)}\n\n"
                
                # --- 处理 LLM 的流式输出 ---
                elif kind == "on_chat_model_stream":
                    data = event["data"]
                    chunk = data.get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        content_chunk = chunk.content
                        # 如果是 Writer 节点，收集草稿内容
                        if name == "writer":
                            current_draft_content += content_chunk
                        yield f"data: {json.dumps({'type': 'token', 'content': content_chunk}, ensure_ascii=False)}\n\n"
                        
                # --- 处理工具结束事件 ---
                elif kind == "on_tool_end":
                    yield f"data: {json.dumps({'type': 'status', 'content': '✅ 搜索完成，正在整理结果...'}, ensure_ascii=False)}\n\n"

            # 工作流结束
            yield f"data: {json.dumps({'type': 'status', 'content': '🎉 工作流执行完毕！'}, ensure_ascii=False)}\n\n"
            
            # 保存最终草稿到数据库（只保存最后一版）
            if current_draft_content:
                try:
                    await save_report(topic=task, content=current_draft_content, db=db, user_id=current_user.id)
                    yield f"data: {json.dumps({'type': 'status', 'content': '💾 报告已保存到数据库'}, ensure_ascii=False)}\n\n"
                except Exception as db_e:
                    print(f"数据库保存失败: {db_e}")
                    yield f"data: {json.dumps({'type': 'error', 'content': f'数据库保存失败: {str(db_e)}'}, ensure_ascii=False)}\n\n"

            yield "data: [DONE]\n\n"
            
        except Exception as e:
            print(f"发生错误: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history")
async def get_history_reports(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """
    获取历史报告列表
    """
    reports = await get_history_report_list(db, current_user.id)
    return {
        "success": True,
        "message": "历史报告列表获取成功",
        "data": [
            {
                "id": report.id,
                "topic": report.topic,
                "content": report.content,
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
            for report in reports
        ]
    }

@router.get("/history/{report_id}")
async def get_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个报告的详细信息
    """
    reports = await get_history_report_list(db, current_user.id)
    for report in reports:
        if report.id == report_id:
            return {
                "success": True,
                "data": {
                    "id": report.id,
                    "topic": report.topic,
                    "content": report.content,
                    "created_at": report.created_at.isoformat() if report.created_at else None
                }
            }
    return {"success": False, "message": "报告不存在"}

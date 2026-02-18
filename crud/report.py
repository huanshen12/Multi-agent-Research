from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.report import Report


async def save_report(topic: str, content: str, db: AsyncSession, user_id: int):
    """保存报告到数据库"""
    report = Report(topic=topic, content=content, user_id=user_id)
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

async def get_history_report_list(db: AsyncSession, user_id: int, report_id: int = None):
    """根据用户ID获取历史报告列表"""
    if report_id:
        result = await db.execute(
            select(Report).where(
                Report.user_id == user_id,
                Report.id == report_id
            )
        )
    else:
        result = await db.execute(
            select(Report).where(Report.user_id == user_id).order_by(Report.created_at.desc())
        )
    return result.scalars().all()

async def get_all_topics(db: AsyncSession, user_id: int):
    """获取所有报告的标题（topic）"""
    result = await db.execute(
        select(Report.topic).where(Report.user_id == user_id).order_by(Report.created_at.desc())
    )
    return result.scalars().all()

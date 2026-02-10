from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

# 数据库连接配置

DATABASE_URL = "mysql+aiomysql://root:123456@localhost/agent_db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_report(topic: str, content: str):
    """保存报告到数据库"""
    async with AsyncSessionLocal() as session:
        try:
            # 确保数据库表存在
            await init_db()
            
            report = Report(topic=topic, content=content)
            session.add(report)
            await session.commit()
            await session.refresh(report)
            print(f"报告已保存，ID: {report.id}")
            return report
        except Exception as e:
            print(f"保存报告失败: {e}")
            await session.rollback()
        finally:
            await session.close()

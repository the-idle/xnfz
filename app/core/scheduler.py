# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.db.session import SessionLocal
from app.models.assessment_management import AssessmentResult

# 配置日志
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

# 创建一个后台调度器实例
scheduler = BackgroundScheduler(timezone="UTC") # 使用 UTC 作为调度器的基准时区

def force_submit_assessment_session(result_id: int):
    """
    这是我们的核心任务函数：强制提交一个考核会话。
    """
    print(f"Executing force_submit task for session_id: {result_id} at {datetime.now(timezone.utc)}")
    
    db: Session = SessionLocal()
    try:
        # 查找仍然在进行中的考核会话
        result = db.query(AssessmentResult).filter(
            AssessmentResult.id == result_id,
            AssessmentResult.end_time == None
        ).first()

        if result:
            # 如果找到了，就设置其结束时间
            result.end_time = datetime.now(timezone.utc)
            db.add(result)
            db.commit()
            print(f"Successfully force-submitted session_id: {result_id}")
        else:
            print(f"Session_id: {result_id} already finished or not found. Skipping.")
            
    finally:
        db.close()

def schedule_auto_submit(result_id: int, run_time: datetime):
    """
    一个辅助函数，用于添加一个新的“自动交卷”任务。
    :param result_id: 要交卷的会话 ID。
    :param run_time: 任务执行的 UTC 时间。
    """
    job_id = f"auto_submit_{result_id}"
    print(f"Scheduling job '{job_id}' to run at {run_time}")
    scheduler.add_job(
        force_submit_assessment_session,
        'date',
        run_date=run_time,
        args=[result_id],
        id=job_id,
        replace_existing=True
    )
# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.db.session import SessionLocal
from app.models.assessment_management import AssessmentResult
from app.core.config import settings

# 配置日志
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.WARNING)  # 减少日志输出

# 配置调度器
jobstores = {
    # 持久化 JobStore，避免服务重启后丢失任务
    'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
}
executors = {
    'default': ThreadPoolExecutor(max_workers=50)  # 提升并发调度能力
}
job_defaults = {
    'coalesce': True,  # 合并错过的任务
    'max_instances': 5,  # 允许同一任务最多5个实例并发
    'misfire_grace_time': 300  # 任务错过后300秒内仍可执行（提升容错）
}

# 创建一个后台调度器实例
scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="UTC"
)

def force_submit_assessment_session(result_id: int):
    """
    这是我们的核心任务函数：强制提交一个考核会话。
    """
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
            logging.info(f"Force-submitted session_id: {result_id}")

    except Exception as e:
        logging.error(f"Error force-submitting session {result_id}: {e}")
        db.rollback()
    finally:
        db.close()

def schedule_auto_submit(result_id: int, run_time: datetime):
    """
    一个辅助函数，用于添加一个新的"自动交卷"任务。
    :param result_id: 要交卷的会话 ID。
    :param run_time: 任务执行的 UTC 时间。
    """
    job_id = f"auto_submit_{result_id}"
    try:
        scheduler.add_job(
            force_submit_assessment_session,
            'date',
            run_date=run_time,
            args=[result_id],
            id=job_id,
            replace_existing=True,
            timezone="UTC",
        )
    except Exception as e:
        logging.error(f"Failed to schedule job {job_id}: {e}")


def force_submit_expired_sessions(assessment_id: int = None):
    """
    批量强制提交已过期但未交卷的会话
    用于处理定时器失效的情况
    """
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # 查询所有已过期但未交卷的会话
        query = db.query(AssessmentResult).filter(
            AssessmentResult.end_time == None
        )

        if assessment_id:
            query = query.filter(AssessmentResult.assessment_id == assessment_id)

        # 获取这些会话关联的考核，检查是否已过期
        from app.models.assessment_management import Assessment
        expired_results = []

        for result in query.all():
            assessment = db.query(Assessment).filter(Assessment.id == result.assessment_id).first()
            if assessment:
                # 将考核结束时间转为 UTC 比较
                import pytz
                beijing_tz = pytz.timezone('Asia/Shanghai')
                end_time_utc = beijing_tz.localize(assessment.end_time).astimezone(timezone.utc)

                if now > end_time_utc:
                    expired_results.append(result)

        # 批量更新
        count = 0
        for result in expired_results:
            result.end_time = datetime.now(timezone.utc)
            db.add(result)
            count += 1

        db.commit()
        logging.info(f"Force-submitted {count} expired sessions")
        return count

    except Exception as e:
        logging.error(f"Error in force_submit_expired_sessions: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def register_housekeeping_jobs():
    """
    注册周期性兜底任务，防止因任务丢失或调度延迟导致未交卷。
    """
    try:
        # 每分钟兜底扫描一次，确保超时会话被提交
        scheduler.add_job(
            force_submit_expired_sessions,
            "interval",
            minutes=1,
            id="force_submit_expired_sessions",
            replace_existing=True,
        )
    except Exception as e:
        logging.error(f"Failed to register housekeeping job: {e}")
# app/api/endpoints/results.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Any
from app import schemas
from app.api import deps
from app.models import user_management as user_models
from app.crud.crud_assessment_result import crud_assessment_result
from app.schemas.response import UnifiedResponse
from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from app.models.assessment_management import AssessmentResult, AnswerLog
from app.models.question_management import Question, Option

router = APIRouter()

@router.get(
    "/assessments/{assessment_id}/results/",
    response_model=UnifiedResponse[Any]
)
def read_assessment_results(
    assessment_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    获取一场考核的所有考生成绩详情 (需要管理员权限)
    支持分页：skip 和 limit 参数
    """
    # 获取总数
    total = crud_assessment_result.get_count_by_assessment(db=db, assessment_id=assessment_id)

    # 获取分页数据
    results = crud_assessment_result.get_multi_by_assessment(
        db=db, assessment_id=assessment_id, skip=skip, limit=limit
    )

    # 手动组装数据以匹配 AssessmentResultDetail schema
    detailed_results = []
    for res in results:
        detailed_results.append({
            "id": res.id,
            "total_score": res.total_score,
            "start_time": res.start_time,
            "end_time": res.end_time,
            "examinee_identifier": res.examinee.identifier if res.examinee else "Unknown",
            "answer_logs": [] # 列表页不需要加载详细题目，留空以提升性能
        })

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "items": detailed_results,
            "total": total
        }
    }

# 2. 获取详情接口 (修复点：确保路径是 /assessment-results/{result_id})
@router.get(
    "/assessment-results/{result_id}",
    response_model=UnifiedResponse[schemas.AssessmentResultDetail]
)
def read_single_assessment_result(
    result_id: int,
    db: Session = Depends(deps.get_db),
    # current_user: user_models.User = Depends(deps.get_current_user)
):
    """
    根据ID获取单次考核详情 (详情视图，包含题目信息)
    """
    # 1. 级联查询：结果 -> 日志 -> 题目 -> 选项
    result = (
        db.query(AssessmentResult)
        .options(
            selectinload(AssessmentResult.examinee),
            selectinload(AssessmentResult.answer_logs)
            .selectinload(AnswerLog.question)
            .selectinload(Question.options)
        )
        .filter(AssessmentResult.id == result_id)
        .first()
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="未找到指定的考核结果。")
    
    # 2. 手动组装数据
    answer_logs_details = []
    
    # 按题目ID排序，保证展示顺序稳定
    sorted_logs = sorted(result.answer_logs, key=lambda x: x.question_id)

    for log in sorted_logs:
        # 处理 selected_option_ids (兼容 list 和 json string)
        selected_ids = []
        if log.selected_option_ids:
            if isinstance(log.selected_option_ids, list):
                selected_ids = log.selected_option_ids
            elif isinstance(log.selected_option_ids, str):
                try:
                    selected_ids = json.loads(log.selected_option_ids)
                except:
                    selected_ids = []

        # 基础日志数据
        log_data = {
            "question_id": log.question_id,
            "score_awarded": log.score_awarded,
            "answered_at": log.answered_at,
            "selected_option_ids": selected_ids,
            "question": None # 默认为 None
        }

        # 注入题目详情 (Snapshoting)
        if log.question:
            log_data["question"] = {
                "prompt": log.question.prompt,
                "question_type": log.question.question_type,
                "score": log.question.score,
                "options": [
                    {
                        "id": opt.id, 
                        "option_text": opt.option_text, 
                        "is_correct": opt.is_correct
                    } 
                    # 选项也排个序
                    for opt in sorted(log.question.options, key=lambda x: x.id)
                ]
            }
        
        answer_logs_details.append(log_data)

    detailed_result = {
        "id": result.id,
        "total_score": result.total_score,
        "start_time": result.start_time,
        "end_time": result.end_time,
        "examinee_identifier": result.examinee.identifier if result.examinee else "Unknown",
        "answer_logs": answer_logs_details
    }
    
    return {"code": 200, "msg": "success", "data": detailed_result}
"Interview repository - 5 tables CRUD."
from datetime import datetime
from typing import Any
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.interview_session import InterviewSession
from app.models.entities.interview_question import InterviewQuestion
from app.models.entities.interview_answer import InterviewAnswer
from app.models.entities.interview_report import InterviewReport
from app.models.entities.resume_optimization import ResumeOptimization

async def create_session(db: AsyncSession, s: InterviewSession) -> InterviewSession:
    db.add(s); await db.flush(); return s

async def get_session_by_id(db: AsyncSession, sid: int) -> InterviewSession | None:
    r = await db.execute(select(InterviewSession).where(InterviewSession.id == sid, InterviewSession.deleted_at == "0"))
    return r.scalar_one_or_none()

async def update_session_status(db: AsyncSession, sid: int, status: str, finished_at=None):
    v = {"status": status}
    if finished_at is not None: v["finished_at"] = finished_at
    await db.execute(update(InterviewSession).where(InterviewSession.id == sid).values(**v))
    await db.flush()

async def create_question(db: AsyncSession, q: InterviewQuestion) -> InterviewQuestion:
    db.add(q); await db.flush(); return q

async def get_question_by_id(db: AsyncSession, qid: int) -> InterviewQuestion | None:
    r = await db.execute(select(InterviewQuestion).where(InterviewQuestion.id == qid, InterviewQuestion.deleted_at == "0"))
    return r.scalar_one_or_none()

async def list_questions_by_session(db: AsyncSession, sid: int) -> list[InterviewQuestion]:
    r = await db.execute(select(InterviewQuestion).where(InterviewQuestion.session_id == sid, InterviewQuestion.deleted_at == "0").order_by(InterviewQuestion.order_no))
    return list(r.scalars().all())

async def list_bank_questions(db: AsyncSession, question_type=None, page=1, size=20):
    cond = [InterviewQuestion.is_bank_visible == True, InterviewQuestion.deleted_at == "0"]
    if question_type: cond.append(InterviewQuestion.question_type == question_type)
    total = (await db.execute(select(func.count()).select_from(InterviewQuestion).where(*cond))).scalar() or 0
    off = (page - 1) * size
    r = await db.execute(select(InterviewQuestion).where(*cond).order_by(InterviewQuestion.order_no).offset(off).limit(size))
    return list(r.scalars().all()), total

async def create_answer(db: AsyncSession, a: InterviewAnswer) -> InterviewAnswer:
    db.add(a); await db.flush(); return a

async def list_answers_by_session(db: AsyncSession, sid: int) -> list[InterviewAnswer]:
    r = await db.execute(select(InterviewAnswer).join(InterviewQuestion, InterviewAnswer.question_id == InterviewQuestion.id).where(InterviewQuestion.session_id == sid, InterviewAnswer.deleted_at == "0", InterviewQuestion.deleted_at == "0").order_by(InterviewQuestion.order_no))
    return list(r.scalars().all())

async def create_report(db: AsyncSession, r: InterviewReport) -> InterviewReport:
    db.add(r); await db.flush(); return r

async def get_report_by_session(db: AsyncSession, sid: int) -> InterviewReport | None:
    r = await db.execute(select(InterviewReport).where(InterviewReport.session_id == sid, InterviewReport.deleted_at == "0"))
    return r.scalar_one_or_none()

async def create_optimization(db: AsyncSession, o: ResumeOptimization) -> ResumeOptimization:
    db.add(o); await db.flush(); return o

async def get_optimization_by_resume(db: AsyncSession, rid: int) -> ResumeOptimization | None:
    r = await db.execute(select(ResumeOptimization).where(ResumeOptimization.resume_id == rid, ResumeOptimization.deleted_at == "0"))
    return r.scalar_one_or_none()

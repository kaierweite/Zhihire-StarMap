"Interview service - AI orchestration."
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.interview.prompts import SYSTEM_QUESTION_GEN, SYSTEM_ANSWER_SCORE, SYSTEM_REPORT_GEN, build_question_prompt, build_score_prompt, build_report_prompt
from app.infrastructure.llm.deepseek_client import deepseek_client
from app.models.entities.interview_session import InterviewSession
from app.models.entities.interview_question import InterviewQuestion
from app.models.entities.interview_answer import InterviewAnswer
from app.models.entities.interview_report import InterviewReport
from app.models.schemas.interview import InterviewQuestionItem, InterviewStartResponse, InterviewMessageResponse, InterviewReportResponse, QuestionBankItem
from app.repositories import interview_repository
from app.services.errors import BusinessError

logger = logging.getLogger(__name__)
_DEFAULT_QUESTIONS = 5

async def start_interview(db, user_id, occupation_role_id, job_id=None):
    session = InterviewSession(user_id=user_id, job_id=job_id, occupation_role_id=occupation_role_id, status="IN_PROGRESS", started_at=datetime.now())
    session = await interview_repository.create_session(db, session)
    try:
        qdata = await _call_llm_question(f"role_{occupation_role_id}", 0)
    except Exception:
        logger.warning("LLM q fail, using fallback")
        qdata = {"question": "\u8bf7\u7b80\u8981\u4ecb\u7ecd\u4e00\u4e0b\u4f60\u81ea\u5df1\u4ee5\u53ca\u4e0e\u76ee\u6807\u5c97\u4f4d\u76f8\u5173\u7684\u7ecf\u9a8c\u3002", "type": "BEHAVIORAL"}
    question = InterviewQuestion(session_id=session.id, question_type=qdata.get("type", "BEHAVIORAL"), content=qdata.get("question", ""), order_no=1, is_bank_visible=False)
    question = await interview_repository.create_question(db, question)
    await db.commit()
    return InterviewStartResponse(session_id=session.id, status="IN_PROGRESS", first_question=InterviewQuestionItem(question_id=question.id, content=question.content, question_type=question.question_type, order_no=1))

async def submit_answer(db, user_id, session_id, question_id, answer_text):
    session = await interview_repository.get_session_by_id(db, session_id)
    if session is None or session.user_id != user_id: raise BusinessError(404, "\u9762\u8bd5\u4f1a\u8bdd\u4e0d\u5b58\u5728")
    if session.status != "IN_PROGRESS": raise BusinessError(400, "\u9762\u8bd5\u5df2\u7ed3\u675f")
    question = await interview_repository.get_question_by_id(db, question_id)
    if question is None or question.session_id != session_id: raise BusinessError(404, "\u95ee\u9898\u4e0d\u5b58\u5728")
    try:
        sr = await _call_llm_score(question.content, answer_text)
    except Exception:
        logger.warning("LLM score fail, using mock")
        sr = {"score": 75, "feedback": "\u56de\u7b54\u57fa\u672c\u5408\u7406\u3002", "matched_points": [], "missed_points": [], "is_final_question": False}
    answer = InterviewAnswer(question_id=question_id, content=answer_text, ai_score=sr.get("score", 0), ai_feedback=sr.get("feedback", ""), matched_points=sr.get("matched_points", []), missed_points=sr.get("missed_points", []), answered_at=datetime.now())
    await interview_repository.create_answer(db, answer)
    questions = await interview_repository.list_questions_by_session(db, session_id)
    answers = await interview_repository.list_answers_by_session(db, session_id)
    answered_count = len(answers)
    is_final = sr.get("is_final_question", False) or answered_count >= _DEFAULT_QUESTIONS
    if is_final:
        await interview_repository.update_session_status(db, session_id, "COMPLETED", finished_at=datetime.now())
        await db.commit()
        try: await _generate_report(db, session_id, questions, answers)
        except Exception: logger.warning("Report gen failed")
        return InterviewMessageResponse(next_question=None, overall_score=answer.ai_score, is_finished=True)
    qa_history = [{"question": q.content, "answer": a.content, "score": a.ai_score, "feedback": a.ai_feedback} for q, a in zip(questions, answers)]
    try:
        nq = await _call_llm_question(f"session_{session_id}", answered_count, qa_history)
    except Exception:
        logger.warning("LLM next q fail")
        nq = {"question": "\u8bf7\u5206\u4eab\u4e00\u6b21\u4f60\u89e3\u51b3\u590d\u6742\u95ee\u9898\u7684\u7ecf\u5386\u3002", "type": "SITUATIONAL"}
    nq_entity = InterviewQuestion(session_id=session_id, question_type=nq.get("type", "TECHNICAL"), content=nq.get("question", ""), order_no=answered_count + 1, is_bank_visible=False)
    nq_entity = await interview_repository.create_question(db, nq_entity)
    await db.commit()
    return InterviewMessageResponse(next_question=InterviewQuestionItem(question_id=nq_entity.id, content=nq_entity.content, question_type=nq_entity.question_type, order_no=answered_count + 1), overall_score=None, is_finished=False)

async def get_report(db, user_id, session_id):
    session = await interview_repository.get_session_by_id(db, session_id)
    if session is None or session.user_id != user_id: raise BusinessError(404, "\u9762\u8bd5\u4f1a\u8bdd\u4e0d\u5b58\u5728")
    report = await interview_repository.get_report_by_session(db, session_id)
    if report is None: raise BusinessError(404, "\u62a5\u544a\u5c1a\u672a\u751f\u6210")
    return InterviewReportResponse(session_id=session_id, overall_score=report.overall_score, radar=report.radar, feedback=report.feedback, created_at=report.created_at)

async def query_question_bank(db, question_type=None, page=1, size=20):
    questions, total = await interview_repository.list_bank_questions(db, question_type=question_type, page=page, size=size)
    items = [QuestionBankItem(id=q.id, question_type=q.question_type, content=q.content, order_no=q.order_no) for q in questions]
    return items, total

async def _call_llm_question(role_name, questions_so_far, qa_history=None):
    prompt = build_question_prompt(role_name, questions_so_far, qa_history)
    resp = await deepseek_client.chat([{"role": "system", "content": SYSTEM_QUESTION_GEN}, {"role": "user", "content": prompt}], temperature=0.7, max_tokens=500)
    return _parse_json(resp, {"question": "", "type": "TECHNICAL"})

async def _call_llm_score(question, answer):
    prompt = build_score_prompt(question, answer)
    resp = await deepseek_client.chat([{"role": "system", "content": SYSTEM_ANSWER_SCORE}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=1000)
    return _parse_json(resp, {"score": 75, "feedback": "", "matched_points": [], "missed_points": [], "is_final_question": False})

async def _generate_report(db, session_id, questions, answers):
    qa_pairs = [{"question": q.content, "answer": a.content, "score": a.ai_score, "feedback": a.ai_feedback} for q, a in zip(questions, answers)]
    try:
        prompt = build_report_prompt(qa_pairs)
        resp = await deepseek_client.chat([{"role": "system", "content": SYSTEM_REPORT_GEN}, {"role": "user", "content": prompt}], temperature=0.3, max_tokens=2000)
        rd = _parse_json(resp, {"overall_score": 75, "radar": {"communication": 70, "technical": 75, "problem_solving": 70, "culture_fit": 75, "depth": 70}, "feedback": {"strengths": [], "weaknesses": [], "suggestions": ""}})
    except Exception:
        logger.warning("LLM report fail, using defaults")
        rd = {"overall_score": 75, "radar": {"communication": 70, "technical": 75, "problem_solving": 70, "culture_fit": 75, "depth": 70}, "feedback": {"strengths": [], "weaknesses": [], "suggestions": "\u9762\u8bd5\u5b8c\u6210\uff0c\u5efa\u8bae\u7ee7\u7eed\u52a0\u5f3a\u76f8\u5173\u77e5\u8bc6\u5b66\u4e60\u3002"}}
    avg_score = sum(a.ai_score or 0 for a in answers) / max(len(answers), 1)
    report = InterviewReport(session_id=session_id, overall_score=rd.get("overall_score", avg_score), radar=rd.get("radar", {}), feedback=rd.get("feedback", {}))
    await interview_repository.create_report(db, report)
    await db.commit()

def _parse_json(response, default):
    try:
        t = response.strip()
        if t.startswith("```json"): t = t[7:]
        if t.endswith("```"): t = t[:-3]
        return json.loads(t.strip())
    except Exception:
        logger.warning("JSON parse fail, using defaults")
        return default

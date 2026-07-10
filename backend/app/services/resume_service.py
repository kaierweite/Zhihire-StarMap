"""?????????

???????CRUD ? AI ?????
"""
import json
import os
from typing import Any

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.core.parsing import extractor
from app.infrastructure.llm.deepseek_client import deepseek_client
from app.infrastructure.storage.file_store import file_store
from app.models.entities.resume import Resume
from app.models.entities.upload_file import UploadFile as UploadFileEntity
from app.models.entities.parse_task import ParseTask
from app.models.entities.user import User
from app.models.schemas.resume import (
    OptimizeResult,
    OptimizeSuggestion,
    ResumeDetail,
    ResumeListItem,
    ResumeUploadResult,
    TaskStatus,
)
from app.repositories import (
    upload_file_repository,
    resume_repository,
    parse_task_repository,
)
from app.services.errors import BusinessError
from app.db.session import AsyncSessionLocal

# ????
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES: set[str] = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


async def upload_resume(
    db: AsyncSession,
    user: User,
    file: UploadFile,
    title: str | None,
) -> ResumeUploadResult:
    """????????? resume ????????

    Args:
        db: ??????
        user: ?????
        file: ?????
        title: ?????

    Returns:
        ResumeUploadResult: ?? resume_id, file_id, task_id?

    Raises:
        BusinessError: ????/???????
    """
    # 1. ????
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise BusinessError(400, "??????????? 10MB?")

    mime_type = file.content_type or ""
    if mime_type not in ALLOWED_MIME_TYPES:
        raise BusinessError(400, f"????????: {mime_type}???? PDF/DOC/DOCX")

    # ??????????
    await file.seek(0)

    # 2. ???????
    access_path = await file_store.save(file, subdir="resumes")
    stored_name = os.path.basename(access_path)

    # 3. ?? upload_file ??
    upload_entity = UploadFileEntity(
        original_name=file.filename or "untitled",
        stored_name=stored_name,
        path=access_path,
        size=file_size,
        mime_type=mime_type,
        uploader_id=user.id,
    )
    upload_entity = await upload_file_repository.create(db, upload_entity)

    # 4. ?? resume ??
    resume_title = title or file.filename or "?????"
    resume = Resume(
        user_id=user.id,
        file_id=upload_entity.id,
        title=resume_title,
    )
    resume = await resume_repository.create(db, resume)

    # 5. ?? parse_task (WAITING)
    task = ParseTask(
        file_id=upload_entity.id,
        user_id=user.id,
        status="WAITING",
        result=None,
    )
    task = await parse_task_repository.create(db, task)

    await db.commit()

    return ResumeUploadResult(
        resume_id=resume.id,
        file_id=upload_entity.id,
        task_id=task.id,
        title=resume_title,
    )


async def list_resumes(
    db: AsyncSession,
    user: User,
    page: int = 1,
    size: int = 20,
) -> tuple[list[ResumeListItem], int]:
    """????????????????

    Returns:
        (records, total)
    """
    rows, total = await resume_repository.list_by_user(db, user.id, page, size)
    items = [
        ResumeListItem(
            id=r.id, title=r.title, status=r.status,
            created_at=r.created_at, updated_at=r.updated_at,
        )
        for r in rows
    ]
    # Batch-populate file_name from upload_file
    file_ids = [r.file_id for r in rows if r.file_id is not None]
    if file_ids:
        from app.repositories.upload_file_repository import list_by_ids as _list_file_ids
        name_map = await _list_file_ids(db, file_ids)
        for item in items:
            for row in rows:
                if row.id == item.id and row.file_id is not None and row.file_id in name_map:
                    item.file_name = name_map[row.file_id]
                    break
    return items, total


async def get_resume_detail(db: AsyncSession, user: User, resume_id: int) -> ResumeDetail:
    """????????????

    Args:
        db: ??????
        user: ?????
        resume_id: ?????

    Returns:
        ResumeDetail: ?????

    Raises:
        BusinessError: ????????????
    """
    resume = await resume_repository.get_by_user_and_id(db, resume_id, user.id)
    if resume is None:
        raise BusinessError(404, "?????")

    parsed = None
    if resume.content_text:
        try:
            parsed = json.loads(resume.content_text)
        except (json.JSONDecodeError, TypeError):
            pass

    return ResumeDetail(
        id=resume.id,
        user_id=resume.user_id,
        file_id=resume.file_id,
        title=resume.title,
        content_text=resume.content_text,
        parsed=parsed,
        status=resume.status,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


def _deep_merge(content_text: str | None, user_json_str: str | None) -> str:
    """Deep-merge user-edited JSON into existing content_text, preserving system-derived fields.

    When the user edits parsed resume content via PUT, only the editable fields
    (name, education, skills names, etc.) are sent back. This function merges the
    user's changes into the existing JSON while preserving system-derived fields
    like skill_id and category in the skills array (matched by skill name).
    """
    if user_json_str is None:
        return content_text if content_text is not None else "{}"

    try:
        old = json.loads(content_text) if content_text else {}
        user_data = json.loads(user_json_str) if isinstance(user_json_str, str) else {}
    except (json.JSONDecodeError, TypeError):
        return user_json_str if isinstance(user_json_str, str) else "{}"

    for k, v in user_data.items():
        if isinstance(v, list) and k == "skills" and isinstance(old.get(k), list):
            old_skills = {s.get("name"): s for s in old[k] if s.get("name")}
            merged_skills = []
            for usr_skill in v:
                name = usr_skill.get("name")
                old_skill = old_skills.get(name) if name else None
                if old_skill:
                    merged = dict(usr_skill)
                    merged["skill_id"] = old_skill.get("skill_id")
                    merged["category"] = old_skill.get("category")
                    merged_skills.append(merged)
                else:
                    merged_skills.append(dict(usr_skill))
            old[k] = merged_skills
        elif isinstance(v, list) and isinstance(old.get(k), list):
            old[k] = [dict(item) for item in v]
        elif k.startswith("_"):
            pass
        else:
            old[k] = v

    return json.dumps(old, ensure_ascii=False)


async def update_resume_content(
    db: AsyncSession,
    user: User,
    resume_id: int,
    title: str | None = None,
    content_text: str | None = None,
) -> ResumeDetail:
    """?????????????

    Args:
        db: ??????
        user: ?????
        resume_id: ?????
        title: ??????
        content_text: ??????? JSON ???

    Returns:
        ResumeDetail: ???????
    """
    resume = await resume_repository.get_by_user_and_id(db, resume_id, user.id)
    if resume is None:
        raise BusinessError(404, "?????")

    if title is not None:
        resume.title = title
    if content_text is not None:
        resume.content_text = _deep_merge(resume.content_text, content_text)

    await resume_repository.update(db, resume)
    await db.commit()

    return await get_resume_detail(db, user, resume_id)





async def delete_resume(db: AsyncSession, user: User, resume_id: int) -> None:
    """??????

    Args:
        db: ??????
        user: ?????
        resume_id: ?????
    """
    resume = await resume_repository.get_by_user_and_id(db, resume_id, user.id)
    if resume is None:
        raise BusinessError(404, "?????")

    await resume_repository.soft_delete(db, resume)
    await db.commit()


async def get_task_status(db: AsyncSession, task_id: int) -> TaskStatus:
    """?????????

    Args:
        db: ??????
        task_id: ?????

    Returns:
        TaskStatus: ???????

    Raises:
        BusinessError: ??????
    """
    task = await parse_task_repository.get_by_id(db, task_id)
    if task is None:
        raise BusinessError(404, "???????")

    return TaskStatus(
        task_id=task.id,
        status=task.status,
        result=task.result,
    )


async def optimize_resume(
    db: AsyncSession,
    user: User,
    resume_id: int,
    job_description: str | None = None,
) -> OptimizeResult:
    """AI ???????

    Args:
        db: ??????
        user: ?????
        resume_id: ?????
        job_description: ???????????

    Returns:
        OptimizeResult: ???????
    """
    resume = await resume_repository.get_by_user_and_id(db, resume_id, user.id)
    if resume is None:
        raise BusinessError(404, "?????")

    resume_text = resume.content_text or ""
    prompt = f"??????????????????????????????????\n\n?????\n{resume_text}\n"
    if job_description:
        prompt += f"\n???????\n{job_description}\n"
    prompt += "\n?? JSON ???????????????? section??????current???????suggestion???????relates_to_skill??????????"

    messages = [{"role": "user", "content": prompt}]
    response = await deepseek_client.chat(messages, temperature=0.3, max_tokens=4096)

    suggestions: list[OptimizeSuggestion] = []
    try:
        raw = response.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        items = json.loads(raw)
        if isinstance(items, list):
            for item in items:
                suggestions.append(OptimizeSuggestion(
                    section=item.get("section", ""),
                    current=item.get("current", ""),
                    suggestion=item.get("suggestion", ""),
                    relates_to_skill=item.get("relates_to_skill"),
                ))
    except (json.JSONDecodeError, Exception):
        suggestions.append(OptimizeSuggestion(
            section="??", current="", suggestion=response, relates_to_skill=None,
        ))

    return OptimizeResult(resume_id=resume_id, suggestions=suggestions)

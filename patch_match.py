"""Patch match_service.py to add INTERVIEW_INVITE notification."""
import re

path = r"C:\Users\Administrator\Desktop\Zhihire-StarMap\backend\app\services\match_service.py"

with open(path, encoding="utf-8") as f:
    content = f.read()

# 1. Add import after BusinessError import
import_marker = "from app.services.errors import BusinessError"
if "from app.services.notification_service import send_notification" not in content:
    content = content.replace(
        import_marker,
        import_marker + "\nfrom app.services.notification_service import send_notification",
    )

# 2. Add notification code before the final return in invite_candidate
old_return = (
    '    await db.commit()\n'
    '\n'
    '    return {"record_id": rec.id, "user_id": resume.user_id, "status": "invited"}'
)

new_block = (
    '    await db.commit()\n'
    '\n'
    '    # Send INTERVIEW_INVITE notification to the candidate\n'
    '    try:\n'
    '        company = await company_repository.get_by_company_id(db, company_id)\n'
    '        company_name = company.company_name if company else ""\n'
    '        await send_notification(\n'
    '            db,\n'
    '            user_id=resume.user_id,\n'
    '            title="\u9762\u8bd5\u9080\u8bf7",\n'
    '            type_="INTERVIEW_INVITE",\n'
    '            content=f"{company_name}\u9080\u8bf7\u60a8\u53c2\u52a0\u300c{job.title}\u300d\u5c97\u4f4d\u7684\u9762\u8bd5\uff0c\u8bf7\u53ca\u65f6\u67e5\u770b\u3002",\n'
    '        )\n'
    '    except Exception:\n'
    '        logger.warning("Failed to send INTERVIEW_INVITE notification", exc_info=True)\n'
    '\n'
    '    return {"record_id": rec.id, "user_id": resume.user_id, "status": "invited"}'
)

if old_return in content:
    content = content.replace(old_return, new_block)
    print("Found and replaced invite_candidate return block")
else:
    print("WARNING: Could not find the invite_candidate return block!")
    # Debug: show last 30 lines
    lines = content.split("\n")
    for i, l in enumerate(lines[-30:]):
        print(f"  {len(lines)-30+i}: {l}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done patching match_service.py")

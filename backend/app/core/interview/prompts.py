"Interview prompt templates for DeepSeek."

SYSTEM_QUESTION_GEN = (
    "You are an expert technical interviewer conducting a mock interview. "
    "Generate ONE interview question at a time. "
    "Question types: TECHNICAL, BEHAVIORAL, SITUATIONAL, RESUME_BASED. "
    "Respond in JSON: {"question": "...", "type": "TECHNICAL"}"
)

SYSTEM_ANSWER_SCORE = (
    "You are an expert interview evaluator. Score the candidate's answer. "
    "Respond in JSON: "
    "{"score": 0-100, "feedback": "...", "
    ""matched_points": [], "missed_points": [], "
    ""is_final_question": true/false}"
)

SYSTEM_REPORT_GEN = (
    "You are an expert interview analyst. Generate interview report with "
    "5 dimensions (communication, technical, problem_solving, culture_fit, depth). "
    "Respond in JSON: "
    "{"overall_score": 0-100, "
    ""radar": {"communication": 0-100, ...}, "
    ""feedback": {"strengths": [], "weaknesses": [], "suggestions": "..."}}"
)

def build_question_prompt(role_name: str, questions_so_far: int, qa_history=None):
    prompt = f"Target role: {role_name}\nQuestions so far: {questions_so_far}\n"
    if qa_history:
        prompt += "History:\n"
        for i, qa in enumerate(qa_history):
            prompt += f"Q{i+1}: {qa.get("question", "")}\nA{i+1}: {qa.get("answer", "")}\n"
    prompt += "\nGenerate next interview question."
    return prompt

def build_score_prompt(question: str, answer: str, expected_points=None):
    prompt = f"Question: {question}\nAnswer: {answer}\n"
    if expected_points:
        prompt += f"Expected points: {', '.join(expected_points)}\n"
    prompt += "\nEvaluate this answer."
    return prompt

def build_report_prompt(qa_pairs: list):
    prompt = "Interview transcript:\n\n"
    for i, qa in enumerate(qa_pairs):
        prompt += f"Q{i+1}: {qa.get("question", "")}\n"
        prompt += f"A{i+1}: {qa.get("answer", "")}\n"
        prompt += f"Score: {qa.get("score", "N/A")}\n\n"
    prompt += "Generate comprehensive report."
    return prompt

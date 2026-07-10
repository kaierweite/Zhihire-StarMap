/** Interview module types — mirrors backend schemas (Day08). */

export interface InterviewQuestionItem {
  question_id: number
  content: string
  question_type: 'TECHNICAL' | 'BEHAVIORAL' | 'SITUATIONAL' | 'RESUME_BASED'
  order_no: number
}

export interface InterviewStartRequest {
  occupation_role_id: number
  job_id?: number | null
}

export interface InterviewStartResponse {
  session_id: number
  status: string
  first_question: InterviewQuestionItem | null
}

export interface InterviewMessageRequest {
  session_id: number
  question_id: number
  answer: string
}

export interface InterviewMessageResponse {
  next_question: InterviewQuestionItem | null
  overall_score: number | null
  is_finished: boolean
}

export interface InterviewRadar {
  communication: number
  technical: number
  problem_solving: number
  culture_fit: number
  depth: number
}

export interface InterviewFeedback {
  strengths: string[]
  weaknesses: string[]
  suggestions: string
}

export interface InterviewReportData {
  session_id: number
  overall_score: number | null
  radar: InterviewRadar | null
  feedback: InterviewFeedback | null
  created_at: string | null
}

export interface QuestionBankItem {
  id: number
  question_type: string
  content: string
  order_no: number
}

export interface QuestionBankData {
  records: QuestionBankItem[]
  total: number
  page: number
  size: number
}

export interface OccupRole {
  id: number
  name: string
  category: string
  description: string
}

/** Locally stored session record for recent list */
export interface SessionRecord {
  session_id: number
  role_name: string
  score: number | null
  created_at: string
  is_finished: boolean
}

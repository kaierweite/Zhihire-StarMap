import request from '@/utils/request'
import type { ApiResponse, PageData } from '@/types/api'
import type {
  InterviewStartRequest,
  InterviewStartResponse,
  InterviewMessageRequest,
  InterviewMessageResponse,
  InterviewReportData,
  QuestionBankData,
} from '@/types/interview'

/** 1. 开始面试 */
export function startInterview(data: InterviewStartRequest) {
  return request.post<ApiResponse<InterviewStartResponse>>('/interview/start', data)
}

/** 2. 提交回答 */
export function submitAnswer(data: InterviewMessageRequest) {
  return request.post<ApiResponse<InterviewMessageResponse>>('/interview/message', data)
}

/** 3. 获取面试报告 */
export function getReport(sessionId: number) {
  return request.get<ApiResponse<InterviewReportData>>(`/interview/report/${sessionId}`)
}

/** 4. 查询题库 */
export function queryQuestionBank(params: {
  question_type?: string
  page?: number
  size?: number
}) {
  return request.get<ApiResponse<QuestionBankData>>('/interview/question-bank', { params })
}

/** 辅助：获取职业角色列表 */
export function listOccupRoles() {
  return request.get<ApiResponse<Array<{ id: number; name: string; category: string; description: string }>>>('/graph/roles')
}

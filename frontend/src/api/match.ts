 import request from '@/utils/request'
 import type { ApiResponse } from '@/types/api'
 
 /* ========== Types ========== */
 
 export interface SkillBreakdown {
   score: number
   hit: string[]
   miss: string[]
   detail: string
 }
 
 export interface SimpleDimension {
   score: number
   detail: string
 }
 
 export interface MatchDetailBreakdown {
   skill: SkillBreakdown
   edu: SimpleDimension
   exp: SimpleDimension
   city: SimpleDimension
 }
 
 export interface MatchDetail {
   score: number
   breakdown: MatchDetailBreakdown
   rationale: string
   graph_hints: string[]
 }
 
 export interface JobRecommendation {
   job_id: number
   resume_id: number
   title: string
   company_name: string
   score: number
   match_detail: MatchDetail
 }
 
 export interface CandidateRecommendation {
   job_id: number
   resume_id: number
   user_id: number
   name: string
   score: number
   match_detail: MatchDetail
 }
 
 export interface ApplyRequest {
   job_id: number
   resume_id: number
 }
 
 export interface ApplyResult {
   application_id: number
   status: string
 }
 
 export interface InviteRequest {
   resume_id: number
   job_id: number
 }
 
 export interface InviteResult {
   record_id: number
   user_id: number
   status: string
 }
 
 /* ========== APIs ========== */
 
 /** 求职者获取推荐岗位列表 */
 export function getRecommendedJobs() {
   return request.get<ApiResponse<{ jobs: JobRecommendation[] }>>('/match/jobs')
 }
 
 /** 企业获取某岗位的候选人推荐 */
 export function getCandidates(jobId: number) {
   return request.get<ApiResponse<{ candidates: CandidateRecommendation[] }>>(`/match/candidates/${jobId}`)
 }
 
 /** 求职者投递岗位 */
 export function applyMatchJob(data: ApplyRequest) {
   return request.post<ApiResponse<ApplyResult>>('/match/apply', data)
 }
 
 /** 企业邀请候选人面试 */
 export function inviteCandidate(data: InviteRequest) {
   return request.post<ApiResponse<InviteResult>>('/match/invite', data)
 }

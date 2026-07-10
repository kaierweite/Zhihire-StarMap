/** Graph node from backend API */
export interface GraphNode {
  id: string
  name: string
  category: string | null
  level: number
  symbolSize: number
  itemStyle?: { color: string }
  label?: { show: boolean; formatter: string }
}

/** Graph edge from backend API */
export interface GraphEdge {
  source: string
  target: string
  relation_type: 'PREREQUISITE' | 'INCLUDES' | 'SIMILAR' | 'COMPLEMENTARY'
  weight: number
  lineStyle?: {
    color: string
    width: number
    type: 'solid' | 'dashed' | 'dotted'
    curveness: number
  }
}

/** Gap skill from backend API */
export interface GapSkill {
  skill_name: string
  requirement_level: 'MUST' | 'BETTER' | 'OPTIONAL'
}

/** Graph result (job graph) */
export interface GraphResult {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

/** User graph result with optional gap skills */
export interface UserGraphResult extends GraphResult {
  gap_skills: GapSkill[]
}

/** Occupation role for role selector */
export interface OccupationRole {
  id: number
  name: string
  category: string | null
  description: string | null
}

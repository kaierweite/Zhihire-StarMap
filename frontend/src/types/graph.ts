/** Graph node from backend API */
export interface GraphNode {
  id: string
  name: string
  category: string | null
  level: number
  level_label: 'none' | 'beginner' | 'intermediate' | 'advanced'
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
  lineStyle: {
    color: string
    width: number
    type: 'solid' | 'dashed' | 'dotted'
    curveness: number
    opacity?: number
  }
}

/** Category with color (replaces frontend hardcoded categoryColors) */
export interface CategoryItem {
  name: string
  color: string
}

/** Gap skill from backend API */
export interface GapSkill {
  skill_name: string
  requirement_level: 'MUST' | 'NICE' | 'BONUS'
}

/** Graph result (job or user graph) */
export interface GraphResult {
  nodes: GraphNode[]
  edges: GraphEdge[]
  state: 'empty' | 'ready'
  categories: CategoryItem[]
  sunburst_data?: SunburstNode | null
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

/** Sunburst hierarchical node for ECharts 旭日图 */
export interface SunburstNode {
  name: string
  value?: number
  id?: string
  itemStyle?: { color: string }
  children?: SunburstNode[]
}

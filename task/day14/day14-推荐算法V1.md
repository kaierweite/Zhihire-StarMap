# 第14天开发任务（详细版）

# 项目：智聘星图——基于银河麒麟操作系统的AI智能匹配与能力图谱平台

## 今日目标

实现推荐算法V1版本，基于技能匹配度、经验匹配度、学历匹配度、城市匹配度计算综合评分。

## 今日能力要求

- 推荐算法设计（熟练）
- Python数据处理（熟练）
- scikit-learn基础（了解）

**最终产出：**

```text
ai-service/app/services/
├──recommender.py               # 推荐算法核心
├──matcher/
│   ├──skill_matcher.py         # 技能匹配器
│   ├──experience_matcher.py    # 经验匹配器
│   ├──education_matcher.py     # 学历匹配器
│   └──city_matcher.py          # 城市匹配器
└──models/
    └──match_result.py          # 匹配结果模型

ai-service/app/api/
└──recommend_api.py             # 推荐API

ai-service/tests/
├──test_skill_matcher.py
├──test_experience_matcher.py
└──test_recommender.py
```

---

# 第一阶段：匹配算法设计（2小时）

## 任务1：技能匹配器（权重50%）

```python
# matcher/skill_matcher.py
from typing import List, Set, Dict
import logging

logger = logging.getLogger(__name__)

class SkillMatcher:
    """
    技能匹配度计算
    权重: 50%
    
    算法说明:
    - 计算用户技能与岗位必备技能的交集/并集比
    - 加分技能按50%权重折算
    - 使用Jaccard相似度 + TF调整
    """

    def calculate(
        self,
        user_skills: List[str],
        required_skills: List[str],
        plus_skills: List[str]
    ) -> Dict:
        user_set = set(s.lower() for s in user_skills)
        required_set = set(s.lower() for s in required_skills)
        plus_set = set(s.lower() for s in plus_skills)

        if not required_set and not plus_set:
            return {"score": 0, "detail": "暂无技能要求"}

        # 必备技能匹配（占比70%）
        if required_set:
            required_match = len(user_set & required_set)
            required_total = len(required_set)
            required_score = (required_match / required_total) * 70
        else:
            required_score = 0

        # 加分技能匹配（占比30%）
        if plus_set:
            plus_match = len(user_set & plus_set)
            plus_total = len(plus_set)
            plus_score = (plus_match / plus_total) * 30
        else:
            plus_score = 0

        total_score = required_score + plus_score

        # 找出匹配和缺失的技能
        matched = list((user_set & required_set) | (user_set & plus_set))
        missing = list((required_set - user_set) | (plus_set - user_set))

        logger.info(
            f"技能匹配完成: required_match={required_match}/{required_total}, "
            f"plus_match={plus_match}/{plus_total}, score={total_score:.2f}"
        )

        return {
            "score": round(total_score, 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "detail": {
                "required_match_rate": f"{required_match}/{required_total}",
                "plus_match_rate": f"{plus_match}/{plus_total}"
            }
        }
```

## 任务2：经验匹配器（权重20%）

```python
# matcher/experience_matcher.py
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ExperienceMatcher:
    """
    工作经验匹配度
    权重: 20%
    
    算法说明:
    - 用户经验 >= 岗位要求: 满分
    - 用户经验 < 岗位要求: 按比例扣分（系数0.8）
    - 至少扣到60分（不直接归零）
    """

    def calculate(self, user_years: float, required_years: int) -> Dict:
        if required_years == 0:
            return {"score": 100, "detail": "无经验要求"}

        score = 100
        if user_years < required_years:
            ratio = user_years / required_years
            score = max(60, ratio * 100 * 0.8)

        logger.info(f"经验匹配: user={user_years}y, required={required_years}y, score={score:.2f}")

        return {
            "score": round(score, 2),
            "detail": {
                "user_experience": user_years,
                "required_experience": required_years,
                "gap": max(0, required_years - user_years)
            }
        }
```

## 任务3：学历匹配器（权重20%）

```python
# matcher/education_matcher.py
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class EducationMatcher:
    """
    学历匹配度
    权重: 20%
    
    学历等级:
    博士: 5
    硕士: 4
    本科: 3
    大专: 2
    其他: 1
    """

    EDUCATION_LEVEL = {
        "博士": 5, "硕士": 4, "本科": 3,
        "大专": 2, "中专": 1, "高中": 1, "": 1
    }

    def calculate(self, user_education: str, required_education: str) -> Dict:
        if not required_education:
            return {"score": 100, "detail": "无学历要求"}

        user_level = self.EDUCATION_LEVEL.get(user_education, 1)
        required_level = self.EDUCATION_LEVEL.get(required_education, 3)

        if user_level >= required_level:
            score = 100
        else:
            score = (user_level / required_level) * 80  # 最低80分

        logger.info(f"学历匹配: user={user_education}({user_level}), "
                     f"required={required_education}({required_level}), score={score:.2f}")

        return {
            "score": round(score, 2),
            "detail": {
                "user_education": user_education,
                "required_education": required_education
            }
        }
```

## 任务4：城市匹配器（权重10%）

```python
# matcher/city_matcher.py
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class CityMatcher:
    """
    城市匹配度
    权重: 10%
    
    算法说明:
    - 同城: 100分
    - 同省: 80分
    - 不同省: 60分（考虑到远程/异地求职）
    - 不限制: 100分
    """

    # 省份映射（简化版）
    PROVINCE_MAP = {
        "北京": "北京", "上海": "上海", "广州": "广东", "深圳": "广东",
        "杭州": "浙江", "南京": "江苏", "成都": "四川", "武汉": "湖北",
        "西安": "陕西", "重庆": "重庆", "长沙": "湖南", "郑州": "河南",
        "苏州": "江苏", "天津": "天津", "厦门": "福建", "青岛": "山东",
    }

    def calculate(self, user_city: str, job_city: str) -> Dict:
        if not job_city:
            return {"score": 100, "detail": "城市不限"}

        if not user_city:
            return {"score": 60, "detail": "用户未填写城市"}

        if user_city == job_city:
            score = 100
        elif self.PROVINCE_MAP.get(user_city) == self.PROVINCE_MAP.get(job_city):
            score = 80
        else:
            score = 60

        return {
            "score": score,
            "detail": {
                "user_city": user_city,
                "job_city": job_city
            }
        }
```

---

# 第二阶段：推荐算法核心（1.5小时）

## 任务1：综合评分计算

```python
# recommender.py
from typing import List, Dict, Optional
from matcher.skill_matcher import SkillMatcher
from matcher.experience_matcher import ExperienceMatcher
from matcher.education_matcher import EducationMatcher
from matcher.city_matcher import CityMatcher
import logging

logger = logging.getLogger(__name__)

class Recommender:
    """
    智能推荐算法V1
    
    评分权重:
    - 技能匹配: 50%
    - 经验匹配: 20%
    - 学历匹配: 20%
    - 城市匹配: 10%
    """

    WEIGHTS = {
        "skill": 0.50,
        "experience": 0.20,
        "education": 0.20,
        "city": 0.10
    }

    def __init__(self):
        self.skill_matcher = SkillMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.education_matcher = EducationMatcher()
        self.city_matcher = CityMatcher()

    def calculate_match(
        self,
        user_profile: Dict,
        job_requirements: Dict
    ) -> Dict:
        """
        计算用户-岗位匹配度
        """
        logger.info(f"开始计算匹配度: user={user_profile.get('user_id')}, job={job_requirements.get('job_id')}")

        # 1. 技能匹配度 (50%)
        skill_result = self.skill_matcher.calculate(
            user_skills=user_profile.get("skills", []),
            required_skills=job_requirements.get("required_skills", []),
            plus_skills=job_requirements.get("plus_skills", [])
        )

        # 2. 经验匹配度 (20%)
        experience_result = self.experience_matcher.calculate(
            user_years=user_profile.get("experience_years", 0),
            required_years=job_requirements.get("experience_min", 0)
        )

        # 3. 学历匹配度 (20%)
        education_result = self.education_matcher.calculate(
            user_education=user_profile.get("education", ""),
            required_education=job_requirements.get("education", "")
        )

        # 4. 城市匹配度 (10%)
        city_result = self.city_matcher.calculate(
            user_city=user_profile.get("city", ""),
            job_city=job_requirements.get("city", "")
        )

        # 综合评分
        total_score = (
            skill_result["score"] * self.WEIGHTS["skill"]
            + experience_result["score"] * self.WEIGHTS["experience"]
            + education_result["score"] * self.WEIGHTS["education"]
            + city_result["score"] * self.WEIGHTS["city"]
        )

        result = {
            "total_score": round(total_score, 2),
            "dimensions": {
                "skill": {"score": skill_result["score"], "weight": self.WEIGHTS["skill"]},
                "experience": {"score": experience_result["score"], "weight": self.WEIGHTS["experience"]},
                "education": {"score": education_result["score"], "weight": self.WEIGHTS["education"]},
                "city": {"score": city_result["score"], "weight": self.WEIGHTS["city"]}
            },
            "details": {
                "matched_skills": skill_result.get("matched_skills", []),
                "missing_skills": skill_result.get("missing_skills", []),
                "experience_gap": experience_result.get("detail", {}).get("gap", 0)
            }
        }

        logger.info(f"匹配完成: total_score={total_score:.2f}")
        return result

    def batch_calculate(
        self,
        user_profile: Dict,
        jobs: List[Dict]
    ) -> List[Dict]:
        """批量计算用户与多个岗位的匹配度"""
        results = []
        for job in jobs:
            match = self.calculate_match(user_profile, job)
            results.append({
                "job_id": job.get("job_id"),
                "job_title": job.get("title"),
                "company_name": job.get("company_name"),
                **match
            })

        # 按总分排序
        results.sort(key=lambda x: x["total_score"], reverse=True)
        return results
```

---

# 第三阶段：推荐API（1小时）

## 任务1：推荐API

```python
# api/recommend_api.py
from fastapi import APIRouter, HTTPException
from models.schemas import (
    MatchRequest, BatchMatchRequest,
    MatchResponse, RecommendResponse
)
from services.recommender import Recommender
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/recommend", tags=["智能推荐"])
recommender = Recommender()

@router.post("/match", response_model=MatchResponse)
async def calculate_match(request: MatchRequest):
    """计算用户-岗位单一匹配度"""
    result = recommender.calculate_match(
        request.user_profile.dict(),
        request.job_requirements.dict()
    )
    return MatchResponse(code=200, message="匹配成功", data=result)

@router.post("/batch", response_model=RecommendResponse)
async def batch_recommend(request: BatchMatchRequest):
    """批量计算推荐结果"""
    results = recommender.batch_calculate(
        request.user_profile.dict(),
        request.jobs
    )
    return RecommendResponse(code=200, message="推荐完成", count=len(results), results=results)
```

---

# 第14天验收标准

必须完成：

✅ 技能匹配算法（Jaccard相似度）

✅ 经验匹配算法（比例扣分）

✅ 学历匹配算法（等级对比）

✅ 城市匹配算法（同城/同省）

✅ 4个维度加权综合评分

✅ 批量推荐计算

✅ 按总分排序

✅ 匹配详情（匹配了哪些技能/缺少哪些技能）

✅ 单元测试覆盖

✅ Git已提交

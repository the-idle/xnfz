from typing import Optional

class ScoreCalculator:
    @staticmethod
    def compute(title: str) -> float:
        # 示例评分逻辑：根据标题长度简单打分，供演示使用
        base = 50.0
        bonus = min(len(title), 50) * 1.0
        return base + bonus